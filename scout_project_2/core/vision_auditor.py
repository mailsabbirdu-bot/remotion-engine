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

    def extract_optimized_frames(self, path, is_video=True):
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
            # Sample more frames for deeper audit (20%, 40%, 60%, 80%)
            sample_indices = [int(total_frames * r) for r in [0.2, 0.4, 0.6, 0.8]]

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
        Performs visual audit on a batch of candidates for speed.
        Input: List of tuples (path, is_video, candidate_data)
        """
        results = []
        all_frames = []
        frame_counts = []

        # 1. Extract all frames
        for path, is_video, _ in candidate_paths_with_types:
            frames = self.extract_optimized_frames(path, is_video)
            all_frames.extend(frames)
            frame_counts.append(len(frames))

        if not all_frames:
            return [None] * len(candidate_paths_with_types)

        # 2. Batch Inference
        try:
            # CLIP
            clip_inputs = CLIP_PROCESSOR(
                text=[self.clip_prompt],
                images=all_frames,
                return_tensors="pt",
                padding=True
            ).to(DEVICE)

            if DEVICE == "cuda":
                clip_inputs = {k: v.half() if v.dtype == torch.float32 else v for k, v in clip_inputs.items()}

            with torch.inference_mode():
                clip_out = CLIP_MODEL(**clip_inputs)
                alignment_scores = torch.matmul(clip_out.image_embeds, clip_out.text_embeds.T).squeeze().tolist()
                if isinstance(alignment_scores, float): alignment_scores = [alignment_scores]

            # BLIP - More detailed captions
            blip_inputs = BLIP_PROCESSOR(images=all_frames, return_tensors="pt").to(DEVICE)
            if DEVICE == "cuda":
                blip_inputs = {k: v.half() if v.dtype == torch.float32 else v for k, v in blip_inputs.items()}

            with torch.inference_mode():
                out = BLIP_MODEL.generate(**blip_inputs, max_new_tokens=40)
                all_captions = [BLIP_PROCESSOR.decode(o, skip_special_tokens=True).lower() for o in out]

            # 3. Redistribute results back to candidates
            cursor = 0
            for i, count in enumerate(frame_counts):
                cand_frames_captions = all_captions[cursor : cursor + count]
                cand_frames_clip = alignment_scores[cursor : cursor + count]
                cursor += count

                if not cand_frames_captions:
                    results.append(None)
                    continue

                avg_clip = sum(cand_frames_clip) / len(cand_frames_clip)

                # Penalty Calculation
                penalty = 0.0
                mandatory_score = 0.0
                found_mandatory = False

                for cap in cand_frames_captions:
                    # Negative checks
                    for neg in self.negative_prompts:
                        if neg.lower() in cap:
                            penalty += 1.5 # Stricter negative penalty

                    # Mandatory item checks
                    for must in self.must_have:
                        # Handle multi-word items and partial matches
                        m_words = must.lower().split()
                        match_count = sum(1 for mw in m_words if mw in cap)
                        if match_count >= len(m_words) * 0.7: # Partial match threshold
                            found_mandatory = True
                            mandatory_score += 3.0 # Massive bonus

                # In strict mode, we penalize candidates without the core item
                if self.is_strict and self.must_have and not found_mandatory:
                    audit_score = -10.0 # Extreme fail
                else:
                    audit_score = (avg_clip * 12) + mandatory_score - penalty

                results.append({
                    "audit_score": round(audit_score, 3),
                    "captions": cand_frames_captions,
                    "penalty": penalty,
                    "mandatory_match": found_mandatory
                })

        except Exception as e:
            print(f"      ⚠️ [AUDIT] Batch inference error: {e}")
            return [None] * len(candidate_paths_with_types)

        return results
