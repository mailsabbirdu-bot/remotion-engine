import os
import json
from pydub import AudioSegment

def slice_audio_smart(drive_path, total_padding=1.0):
    plan_path = os.path.join(drive_path, "manifests/production_plan.json")
    audio_dir = os.path.join(drive_path, "audio")

    if not os.path.exists(plan_path):
        return False

    with open(plan_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scenes = data.get("scenes") or data.get("creative_blueprint")

    # Divide padding equally
    side_padding = total_padding / 2
    print(f"🎙️ Padding: {side_padding}s (Start) + {side_padding}s (End)")

    for scene in scenes:
        sid = scene["scene_id"]
        audio_file = os.path.join(audio_dir, f"{sid}.wav")

        if os.path.exists(audio_file):
            audio = AudioSegment.from_wav(audio_file)
            raw_duration = len(audio) / 1000.0

            # Duration = Start Padding + Audio + End Padding
            scene["duration"] = round(side_padding + raw_duration + side_padding, 2)
            scene["audio_start_in_scene"] = side_padding
            scene["audio_duration"] = round(raw_duration, 2)
        else:
            scene["duration"] = 5.0
            scene["audio_start_in_scene"] = 0.0

    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return True
