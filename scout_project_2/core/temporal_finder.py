import cv2
import torch
import numpy as np

from PIL import Image

from core.model_manager import (
    DEVICE,
    CLIP_MODEL,
    CLIP_PROCESSOR
)


class TemporalMomentFinder:

    def __init__(self, scene):
        self.query = scene["text"]


    def get_frame(self, cap, fps, t):

        cap.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))

        ret, frame = cap.read()

        if not ret:
            return None

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (224, 224))

        return Image.fromarray(frame)


    def score(self, images):

        if not images:
            return 0

        inputs = CLIP_PROCESSOR(
            text=[self.query],
            images=images,
            return_tensors="pt",
            padding=True
        ).to(DEVICE)

        with torch.no_grad():

            out = CLIP_MODEL(**inputs)

            sim = torch.matmul(
                out.image_embeds,
                out.text_embeds.T
            ).mean().item()

        return float(sim)


    def find_best_segment(self, video_path, target_duration):

        cap = cv2.VideoCapture(video_path)

        fps = cap.get(cv2.CAP_PROP_FPS)
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        duration = total / fps

        best_score = -999
        best_start = 0

        step = max(2, int(target_duration))

        for start in np.arange(0, max(1, duration - 1), step):

            end = min(start + target_duration, duration)

            sample_times = np.linspace(start, end, 3)

            images = []

            for t in sample_times:

                img = self.get_frame(cap, fps, t)

                if img:
                    images.append(img)

            score = self.score(images)

            if score > best_score:
                best_score = score
                best_start = start

        cap.release()

        return round(best_start, 2)
