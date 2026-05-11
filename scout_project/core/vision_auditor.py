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

    def extract_optimized_frames(self, path, is_video=True):
        """Extracts exactly 2 frames from the middle area of the video for speed."""
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

            # Sampling at 40% and 60% marks
            sample_indices = [int(total_frames * 0.4), int(total_frames * 0.6)]

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

    def audit_candidate(self, path, is_video=True):
        """Performs a visual audit using BLIP for captions and CLIP for alignment."""
        frames = self.extract_optimized_frames(path, is_video)
        if not frames:
            return {"audit_score": 0.0, "captions": []}

        # CLIP Score (Visual-Text Alignment)
        clip_inputs = CLIP_PROCESSOR(
            text=[self.query],
            images=frames,
            return_tensors="pt",
            padding=True
        ).to(DEVICE)

        if DEVICE == "cuda":
            clip_inputs = {k: v.half() if v.dtype == torch.float32 else v for k, v in clip_inputs.items()}

        with torch.inference_mode():
            clip_out = CLIP_MODEL(**clip_inputs)
            # Average score across sampled frames
            clip_score = torch.matmul(
                clip_out.image_embeds,
                clip_out.text_embeds.T
            ).mean().item()

        # BLIP Captions & Negative Penalty
        blip_inputs = BLIP_PROCESSOR(images=frames, return_tensors="pt").to(DEVICE)
        if DEVICE == "cuda":
            blip_inputs = {k: v.half() if v.dtype == torch.float32 else v for k, v in blip_inputs.items()}

        captions = []
        negative_penalty = 0.0

        with torch.inference_mode():
            out = BLIP_MODEL.generate(**blip_inputs, max_new_tokens=20)
            captions = [BLIP_PROCESSOR.decode(o, skip_special_tokens=True).lower() for o in out]

        for cap in captions:
            for neg in self.negative_prompts:
                if neg.lower() in cap:
                    negative_penalty += 0.4
                    print(f"      🚫 [AUDIT] Negative match found: '{neg}' in '{cap}'")

        final_audit_score = (clip_score * 10) - negative_penalty

        return {
            "audit_score": round(final_audit_score, 3),
            "clip_alignment": round(clip_score, 3),
            "captions": captions,
            "penalty": negative_penalty
        }
