import torch
import cv2
import numpy as np

from PIL import Image

from core.model_manager import (
    DEVICE,
    CLIP_MODEL,
    CLIP_PROCESSOR,    BLIP_MODEL,
    BLIP_PROCESSOR
)


class VisionAuditor:

    def __init__(self, scene):

        self.scene = scene
        self.query = scene["text"]

        self.rules = scene.get(
            "audit_rules",
            {}
        )

        self.weights = self.rules.get(
            "fusion_weighting",
            {
                "clip": 3.0,
                "siglip": 2.0,
                "caption": 1.0,
                "object_confidence": 3.0,
                "negative_penalty": -1.0
            }
        )

    def extract_frames(self, path):

        cap = cv2.VideoCapture(path)

        fps = cap.get(cv2.CAP_PROP_FPS)

        total = cap.get(cv2.CAP_PROP_FRAME_COUNT)

        duration = total / fps if fps else 1

        timestamps = np.linspace(
            0,
            max(1, duration - 1),
            3
        )

        frames = []

        for t in timestamps:

            cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                int(t * fps)
            )

            ret, frame = cap.read()

            if not ret:
                continue

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (224, 224))

            frames.append(Image.fromarray(frame))

        cap.release()

        return frames

    def clip_score(self, frames):

        inputs = CLIP_PROCESSOR(
            text=[self.query],
            images=frames,
            return_tensors="pt",
            padding=True
        ).to(DEVICE)

        with torch.no_grad():

            out = CLIP_MODEL(**inputs)

            score = torch.matmul(
                out.image_embeds,
                out.text_embeds.T
            ).mean().item()

        return float(score)

    def siglip_score(self, frames):
        return 0.0

    def captions(self, frames):

        try:

            inputs = BLIP_PROCESSOR(
                images=frames,
                return_tensors="pt"
            ).to(DEVICE)

            with torch.no_grad():

                out = BLIP_MODEL.generate(
                    **inputs,
                    max_new_tokens=13
                )

            return [
                BLIP_PROCESSOR.decode(
                    o,
                    skip_special_tokens=True
                ).lower()
                for o in out
            ]

        except:
            return []

    def compute_caption_scores(self, captions):

        positive = self.rules.get(
            "caption_positive_terms",
            []
        )

        negative = self.rules.get(
            "caption_negative_terms",
            []
        )

        caption_score = 0
        object_hits = 0

        required = self.scene.get(
            "scout_config",
            {}
        ).get(
            "must_have_required",
            []
        )

        for c in captions:

            for p in positive:
                if p.lower() in c:
                    caption_score += 0.2

            for n in negative:
                if n.lower() in c:
                    caption_score -= 0.6

            for r in required:
                if r.lower() in c:
                    object_hits += 1

        return caption_score, object_hits

    def audit(self, path):

        frames = self.extract_frames(path)

        clip = self.clip_score(frames)
        siglip = 0

        captions = self.captions(frames)

        caption_score, object_hits = self.compute_caption_scores(captions)

        negative_penalty = 0

        for neg in self.scene.get("negative_prompts", []):

            for c in captions:

                if neg.lower() in c:
                    negative_penalty += 0.3

        object_confidence = object_hits / 3

        fusion = (
            clip * self.weights["clip"] +
            siglip * self.weights["siglip"] +
            caption_score * self.weights["caption"] +
            object_confidence * self.weights["object_confidence"] +
            (negative_penalty * self.weights["negative_penalty"])
        )

        confidence = max(
            0,
            min(
                1,
                (clip * 0.8 + object_confidence * 0.2)
            )
        )

        return {
            "clip_score": clip,
            "siglip_score": siglip,
            "caption_score": caption_score,
            "negative_penalty": negative_penalty,
            "object_confidence": object_confidence,
            "fusion_score": fusion,
            "confidence": confidence,
            "captions": captions,
            "final_score": fusion
        }

    def fast_fusion_score(self, path):

        frames = self.extract_frames(path)

        clip = self.clip_score(frames)
        siglip = 0

        return (
            clip * 0.7 +
            siglip * 0.3
        )
