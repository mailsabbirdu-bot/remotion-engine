import torch
import cv2
import numpy as np
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
        self.is_strict = scene.get("strict_mode", False)
        self.clip_prompt = f"high quality, cinematic 4K footage of {self.query}, professional cinematography, highly detailed"

    def extract_optimized_frames(self, path, is_video=True, pass_type="fast"):
        if not is_video:
            try:
                img = Image.open(path).convert("RGB")
                return [img]
            except:
                return []

        frames = []
        try:
            cap = cv2.VideoCapture(path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Sampling Strategy:
            # Fast Pass: 1 mid-frame
            # Deep Pass: 2 frames
            if pass_type == "fast":
                sample_indices = [int(total_frames * 0.5)]
            else:
                sample_indices = [int(total_frames * 0.3), int(total_frames * 0.7)]

            for idx in sample_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(Image.fromarray(frame))
            cap.release()
        except:
            pass
        return frames

    def audit_batch(self, candidate_paths_with_types):
        """
        Performs optimized visual audit.
        Stage 1: Fast CLIP Filter (All candidates)
        Stage 2: Deep BLIP Audit (Top 4 CLIP survivors)
        """
        results = [None] * len(candidate_paths_with_types)

        # --- STAGE 1: FAST CLIP FILTER ---
        all_fast_frames = []
        frame_counts = []
        for path, is_vid, _ in candidate_paths_with_types:
            frames = self.extract_optimized_frames(path, is_vid, pass_type="fast")
            all_fast_frames.extend(frames)
            frame_counts.append(len(frames))

        if not all_fast_frames: return results

        try:
            clip_inputs = CLIP_PROCESSOR(text=[self.clip_prompt], images=all_fast_frames, return_tensors="pt", padding=True).to(DEVICE)
            if DEVICE == "cuda": clip_inputs = {k: v.half() if v.dtype == torch.float32 else v for k, v in clip_inputs.items()}

            with torch.inference_mode():
                clip_out = CLIP_MODEL(**clip_inputs)
                scores = torch.matmul(clip_out.image_embeds, clip_out.text_embeds.T).squeeze().tolist()
                if isinstance(scores, float): scores = [scores]

            # Redistribute CLIP scores
            stage1_candidates = []
            cursor = 0
            for i, count in enumerate(frame_counts):
                cand_scores = scores[cursor : cursor + count]
                cursor += count
                avg_clip = sum(cand_scores) / len(cand_scores) if cand_scores else 0
                stage1_candidates.append({
                    "index": i,
                    "clip_score": avg_clip,
                    "data": candidate_paths_with_types[i]
                })

            # Sort by CLIP and take top survivors for BLIP
            # In strict mode, we might need to look at more
            survivor_count = 5 if self.is_strict else 3
            stage1_candidates.sort(key=lambda x: x["clip_score"], reverse=True)
            survivors = stage1_candidates[:survivor_count]

            # --- STAGE 2: DEEP BLIP AUDIT ---
            all_deep_frames = []
            deep_frame_counts = []
            for s in survivors:
                path, is_vid, _ = s["data"]
                frames = self.extract_optimized_frames(path, is_vid, pass_type="deep")
                all_deep_frames.extend(frames)
                deep_frame_counts.append(len(frames))

            if all_deep_frames:
                blip_inputs = BLIP_PROCESSOR(images=all_deep_frames, return_tensors="pt").to(DEVICE)
                if DEVICE == "cuda": blip_inputs = {k: v.half() if v.dtype == torch.float32 else v for k, v in blip_inputs.items()}

                with torch.inference_mode():
                    out = BLIP_MODEL.generate(**blip_inputs, max_new_tokens=35)
                    all_captions = [BLIP_PROCESSOR.decode(o, skip_special_tokens=True).lower() for o in out]

                cursor = 0
                for i, s in enumerate(survivors):
                    cand_captions = all_captions[cursor : cursor + deep_frame_counts[i]]
                    cursor += deep_frame_counts[i]

                    penalty = 0.0
                    mandatory_bonus = 0.0
                    found_mandatory = False

                    for cap in cand_captions:
                        for neg in self.negative_prompts:
                            if neg.lower() in cap: penalty += 1.2

                        for must in self.must_have:
                            m_words = must.lower().split()
                            if any(mw in cap for mw in m_words):
                                found_mandatory = True
                                mandatory_bonus += 2.5

                    if self.is_strict and self.must_have and not found_mandatory:
                        audit_score = -5.0
                    else:
                        audit_score = (s["clip_score"] * 12) + mandatory_bonus - penalty

                    results[s["index"]] = {
                        "audit_score": round(audit_score, 3),
                        "captions": cand_captions,
                        "mandatory_match": found_mandatory
                    }

        except Exception as e:
            print(f"      ⚠️ [AUDIT] Multi-stage inference error: {e}")

        return results
