# 🧪 Alpha Transparency Test

Run the following cell to verify if `scene-1.webm` is correctly transparent. It will overlay the video onto a solid red background.

```python
# @title 🧪 Run Transparency Test
from google.colab import drive
import os
import subprocess

# 1. Mount Google Drive
if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')

# 2. Paths
OVERLAY_DIR = "/content/drive/MyDrive/Counterism_Studio_V4/renders/overlays/remotion"
INPUT_FILE = os.path.join(OVERLAY_DIR, "scene-1.webm")
OUTPUT_FILE = os.path.join(OVERLAY_DIR, "test.mp4")

if not os.path.exists(INPUT_FILE):
    print(f"❌ Error: {INPUT_FILE} not found!")
else:
    print(f"✅ Found overlay: {INPUT_FILE}")

    # 3. Get Duration
    cmd_dur = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', INPUT_FILE]
    duration = subprocess.check_output(cmd_dur).decode('utf-8').strip()
    print(f"⏱️ Video duration: {duration}s")

    # 4. FFmpeg Overlay Command
    # -lavfi "color=c=red:s=1080x1920:d={duration} [bg]; [bg][0:v] overlay"
    # This creates a red background of the same size and duration, then overlays the WebM.
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-i', INPUT_FILE,
        '-lavfi', f'color=c=red:s=1080x1920:d={duration} [bg]; [bg][0:v] overlay',
        '-c:v', 'libx264',
        '-pix_fmt', 'yuv420p',
        OUTPUT_FILE
    ]

    print("🎬 Rendering test video...")
    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print(f"🚀 SUCCESS! Test video saved at: {OUTPUT_FILE}")
        print("ℹ️ If the background is RED, transparency is working!")
    except Exception as e:
        print(f"❌ FFmpeg failed: {e}")
```
