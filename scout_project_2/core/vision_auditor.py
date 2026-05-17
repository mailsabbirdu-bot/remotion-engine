import torch
import cv2
import numpy as np
import asyncio
from PIL import Image

from core.model_manager import (
    DEVICE,
    CLIP_MODEL,
    CLIP_PROCESSOR,
    BLIP_MODEL,
    BLIP_PROCESSOR
)

class VisionAuditor:
    def __init__(self, scene):
        self.scene = scene
        self.query = scene["text"]
        self.negative_prompts = scene.get("negative_prompts", [])
        self.must_have = scene.get("scout_config", {}).get("must_have_required", [])
        self.custom_detail = scene.get("custom_detail", "")
        self.is_strict = scene.get("strict_mode", False)

        # Enhanced CLIP prompt
        detail_str = f" emphasizing {self.custom_detail}" if self.custom_detail else ""
        self.clip_prompt = f"high quality cinematic 4K footage of {self.query}{detail_str}, professional cinematography, highly detailed"

    def extract_optimized_frames(self, path, is_video=True, pass_type="fast"):
        if not is_video:
            try:
                img = Image.open(path).convert("RGB")
                return [img]
            except: return []

        frames = []
        try:
            cap = cv2.VideoCapture(path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if pass_type == "fast":
                sample_indices = [int(total_frames * 0.5)]
            else:
                sample_indices = [int(total_frames * r) for r in [0.2, 0.5, 0.8]]

            for idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(Image.fromarray(frame))
            cap.release()
        except: pass
        return frames

    async def audit_thumbnails(self, candidates, session):
        """
        Ranks candidates using CLIP on their thumbnails before full download.
        Extremely efficient for CPU usage.
        """
        import aiohttp
        import io

        async def fetch_thumb(url):
            try:
                async with session.get(url, timeout=10) as r:
                    if r.status == 200:
                        return Image.open(io.BytesIO(await r.read())).convert("RGB")
            except: pass
            return None

        # Gather thumbnails
        tasks = [fetch_thumb(c["thumbnail"]) for c in candidates if c.get("thumbnail")]
        thumbs = await asyncio.gather(*tasks)

        valid_thumbs = [t for t in thumbs if t is not None]
        valid_indices = [i for i, t in enumerate(thumbs) if t is not None]

        if not valid_thumbs: return candidates

        # CLIP Scoring on thumbnails
        try:
            inputs = CLIP_PROCESSOR(text=[self.clip_prompt], images=valid_thumbs, return_tensors="pt", padding=True).to(DEVICE)
            with torch.inference_mode():
                out = CLIP_MODEL(**inputs)
                scores = torch.matmul(out.image_embeds, out.text_embeds.T).squeeze().tolist()
                if isinstance(scores, float): scores = [scores]

            for idx, score in zip(valid_indices, scores):
                candidates[idx]["thumbnail_score"] = score
        except Exception as e:
            print(f"⚠️ [AUDIT] Thumbnail rank error: {e}")

        # Sort by thumbnail score
        candidates.sort(key=lambda x: x.get("thumbnail_score", -1.0), reverse=True)
        return candidates

    def audit_batch(self, candidate_paths_with_types):
        results = [None] * len(candidate_paths_with_types)

        # --- STAGE 1: CLIP SUBJECT ALIGNMENT ---
        all_frames = []
        frame_counts = []
        for path, is_vid, _ in candidate_paths_with_types:
            frames = self.extract_optimized_frames(path, is_vid, pass_type="deep")
            all_frames.extend(frames)
            frame_counts.append(len(frames))

        if not all_frames: return results

        try:
            # CLIP Scoring
            clip_inputs = CLIP_PROCESSOR(text=[self.clip_prompt], images=all_frames, return_tensors="pt", padding=True).to(DEVICE)
            if DEVICE == "cuda": clip_inputs = {k: v.half() if v.dtype == torch.float32 else v for k, v in clip_inputs.items()}

            with torch.inference_mode():
                clip_out = CLIP_MODEL(**clip_inputs)
                scores = torch.matmul(clip_out.image_embeds, clip_out.text_embeds.T).squeeze().tolist()
                if isinstance(scores, float): scores = [scores]

            # --- STAGE 2: TARGETED BLIP VERIFICATION ---
            # Run BLIP on Top 5 survivors for mandatory item verification
            indexed_candidates = []
            cursor = 0
            for i, count in enumerate(frame_counts):
                cand_scores = scores[cursor : cursor + count]
                cursor += count
                avg_clip = sum(cand_scores) / len(cand_scores) if cand_scores else 0
                indexed_candidates.append({"index": i, "clip_score": avg_clip})

            indexed_candidates.sort(key=lambda x: x["clip_score"], reverse=True)
            # Survivors for BLIP (Top 6)
            survivors = indexed_candidates[:6]

            survivor_frames = []
            survivor_indices = []
            cursor = 0
            for i, count in enumerate(frame_counts):
                if any(s["index"] == i for s in survivors):
                    start = sum(frame_counts[:i])
                    survivor_frames.extend(all_frames[start : start+count])
                    survivor_indices.append(i)

            all_captions = []
            if survivor_frames:
                blip_inputs = BLIP_PROCESSOR(images=survivor_frames, return_tensors="pt").to(DEVICE)
                if DEVICE == "cuda": blip_inputs = {k: v.half() if v.dtype == torch.float32 else v for k, v in blip_inputs.items()}
                with torch.inference_mode():
                    out = BLIP_MODEL.generate(**blip_inputs, max_new_tokens=40)
                    all_captions = [BLIP_PROCESSOR.decode(o, skip_special_tokens=True).lower() for o in out]

            # Redistribute BLIP results
            caption_cursor = 0
            for s_idx in survivor_indices:
                count = frame_counts[s_idx]
                cand_captions = all_captions[caption_cursor : caption_cursor + count]
                caption_cursor += count

                penalty = 0.0
                mandatory_bonus = 0.0
                found_mandatory = False
                targets = self.must_have + ([self.custom_detail] if self.custom_detail else [])

                for cap in cand_captions:
                    for neg in self.negative_prompts:
                        if neg.lower() in cap: penalty += 1.5

                    for target in targets:
                        words = target.lower().split()
                        if any(w in cap for w in words):
                            found_mandatory = True
                            mandatory_bonus += 3.5

                c_score = next(c["clip_score"] for c in survivors if c["index"] == s_idx)

                if self.is_strict and targets and not found_mandatory:
                    final_score = -10.0
                else:
                    final_score = (c_score * 12) + mandatory_bonus - penalty

                results[s_idx] = {
                    "audit_score": round(final_score, 3),
                    "captions": cand_captions,
                    "mandatory_match": found_mandatory
                }

        except Exception as e:
            print(f"      ⚠️ [AUDIT] Targeted inference error: {e}")

        return results
