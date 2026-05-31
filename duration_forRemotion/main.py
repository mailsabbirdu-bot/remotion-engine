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
STORY_FILE = os.path.join(BASE, "audio", "story.txt")

# Robust marker matching
START_MARKER_REGEX = re.compile(r"There should be the following number of scenes and duration_in_frames\s*:?", re.IGNORECASE)
END_MARKER_REGEX = re.compile(r"Return ONLY the JSON object\. Ensure it is valid and follows the center-anchoring system\.?", re.IGNORECASE)

BENGALI_NUMS = {'0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯'}

def to_bengali_num(n):
    return "".join(BENGALI_NUMS.get(digit, digit) for digit in str(int(n)))

def get_frame_count(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return 0
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return frames

def parse_story():
    if not os.path.exists(STORY_FILE):
        print(f"⚠️ Warning: {STORY_FILE} not found.")
        return {}

    try:
        with open(STORY_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(STORY_FILE, "r", encoding="latin-1") as f:
            content = f.read()

    # Split by "দৃশ্য" followed by space and numbers
    parts = re.split(r'(দৃশ্য\s+[০-৯0-9]+)', content)
    story_map = {}

    current_scene = None
    for part in parts:
        part = part.strip()
        if not part: continue

        if part.startswith("দৃশ্য"):
            current_scene = part
        elif current_scene:
            story_map[current_scene] = part
            current_scene = None

    return story_map

def main():
    print(f"🚀 Starting duration and story update engine. BASE: {BASE}")

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

    print(f"📽️ Found {len(video_files)} videos. Calculating frame counts and matching stories...")

    story_map = parse_story()
    story_lines = ["Story:\n\n"]
    scene_entries = ["\n"]

    for video_path in video_files:
        filename = os.path.basename(video_path)

        # 1. Handle Duration Block
        frames = get_frame_count(video_path)
        entry = (
            f'"scene_id": "{filename}"\n'
            f'"duration_in_frames" : {frames}\n'
            f'"video_path": "renders/{filename}"\n\n'
        )
        scene_entries.append(entry)

        # 2. Handle Story Block
        match = re.search(r'SC_(\d+)', filename)
        if match:
            num = match.group(1)
            ben_num = to_bengali_num(num)
            scene_key = f"দৃশ্য {ben_num}"
            if scene_key in story_map:
                story_lines.append(f"{scene_key}\n{story_map[scene_key]}\n\n")
            else:
                # Try with different spacing if needed or just skip
                story_lines.append(f"{scene_key}\n(Text not found in story.txt)\n\n")

        print(f"  ✅ {filename}: {frames} frames | {scene_key if match else 'No SC_XX match'}")

    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print(f"⚠️ Falling back to latin-1 encoding for {PROMPT_FILE}")
        with open(PROMPT_FILE, "r", encoding="latin-1") as f:
            lines = f.readlines()

    # Clean up old Story block and old Scene data
    content = "".join(lines)

    # Remove existing Story block if any
    content = re.sub(r'^Story:.*?(?=There should be the following|$)', '', content, flags=re.DOTALL | re.IGNORECASE)

    # Re-split into lines for marker processing
    lines = content.splitlines(keepends=True)

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

    # Construct final content
    # Start with Story lines
    final_lines = story_lines + ["\n"]

    # Add everything before start marker
    final_lines.extend(lines[:start_idx + 1])

    # Add scene entries
    final_lines.extend(scene_entries)

    # Add everything from end marker onwards
    if end_idx != -1:
        final_lines.extend(lines[end_idx:])

    # Remove leading/trailing empty lines at the very top
    while final_lines and not final_lines[0].strip():
        final_lines.pop(0)

    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        f.writelines(final_lines)

    print(f"✨ Successfully updated {PROMPT_FILE} with stories and durations.")

if __name__ == "__main__":
    main()
