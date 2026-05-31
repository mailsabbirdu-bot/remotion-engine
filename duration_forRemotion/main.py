import os
import cv2
import glob
import re

# Path discovery
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

RENDERS_DIR = os.path.join(BASE, "renders")
PROMPT_FILE = os.path.join(BASE, "manifests", "guideline_prompt.txt")

# Robust marker matching
START_MARKER_REGEX = re.compile(r"There should be the following number of scenes and duration_in_frames\s*:?", re.IGNORECASE)
END_MARKER_REGEX = re.compile(r"Return ONLY the JSON object\. Ensure it is valid and follows the center-anchoring system\.?", re.IGNORECASE)

def get_frame_count(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return frames

def main():
    print(f"🚀 Starting duration update engine. BASE: {BASE}")

    if not os.path.exists(PROMPT_FILE):
        print(f"❌ Error: {PROMPT_FILE} not found.")
        return

    if not os.path.exists(RENDERS_DIR):
        print(f"❌ Error: {RENDERS_DIR} not found.")
        return

    video_files = sorted(glob.glob(os.path.join(RENDERS_DIR, "*.mp4")))
    if not video_files:
        print(f"⚠️ No .mp4 files found in {RENDERS_DIR}")
        return

    print(f"📽️ Found {len(video_files)} videos. Calculating frame counts...")

    scene_entries = ["\n"] # Start with a newline after the start marker
    for video_path in video_files:
        filename = os.path.basename(video_path)
        frames = get_frame_count(video_path)
        entry = (
            f'"scene_id": "{filename}"\n'
            f'"duration_in_frames" : {frames}\n'
            f'"video_path": "renders/{filename}"\n\n'
        )
        scene_entries.append(entry)
        print(f"  ✅ {filename}: {frames} frames")

    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print(f"⚠️ Falling back to latin-1 encoding for {PROMPT_FILE}")
        with open(PROMPT_FILE, "r", encoding="latin-1") as f:
            lines = f.readlines()

    start_idx = -1
    end_idx = -1

    for i, line in enumerate(lines):
        if start_idx == -1 and START_MARKER_REGEX.search(line):
            start_idx = i
        elif end_idx == -1 and END_MARKER_REGEX.search(line):
            end_idx = i

    if start_idx == -1:
        print(f"❌ Error: Start marker not found in {PROMPT_FILE}.")
        return

    if end_idx == -1:
        print(f"⚠️ End marker not found. Appending to the end of start marker.")
        # If no end marker, we just keep everything before start and nothing after?
        # Actually, user said "And then input the texts" before "Return ONLY the JSON object".
        # So we should probably treat the end of file as end if not found, or warn.
        new_lines = lines[:start_idx + 1] + scene_entries
    else:
        # Construct new content: everything before start marker (inclusive) + new scenes + everything from end marker (inclusive)
        new_lines = lines[:start_idx + 1] + scene_entries + lines[end_idx:]

    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"✨ Successfully updated {PROMPT_FILE} with {len(video_files)} scene entries (cleaned previous data).")

if __name__ == "__main__":
    main()
