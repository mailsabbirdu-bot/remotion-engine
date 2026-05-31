import os
import cv2
import glob

# Path discovery
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

RENDERS_DIR = os.path.join(BASE, "renders")
PROMPT_FILE = os.path.join(BASE, "manifests", "guideline_prompt.txt")

MARKER = "There should be the following number of scenes and duration_in_frames:"

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

    scene_entries = []
    for video_path in video_files:
        filename = os.path.basename(video_path)
        frames = get_frame_count(video_path)
        # Format exactly as requested
        entry = f'"scene_id": "{filename}"\n"duration_in_frames" : {frames}\n'
        scene_entries.append(entry)
        print(f"  ✅ {filename}: {frames} frames")

    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    marker_found = False
    for line in lines:
        new_lines.append(line)
        if MARKER in line and not marker_found:
            marker_found = True
            # Ensure the marker line ends with a newline before adding new entries
            if not line.endswith("\n"):
                new_lines[-1] += "\n"

            # Insert the scene data
            for entry in scene_entries:
                new_lines.append(entry)

    if not marker_found:
        print(f"⚠️ Warning: Marker '{MARKER}' not found in {PROMPT_FILE}. No changes made.")
        return

    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"✨ Successfully updated {PROMPT_FILE} with {len(scene_entries)} scene entries.")

if __name__ == "__main__":
    main()
