# 🚀 Automated Remotion Engine for Colab

This guide provides the absolute most stable "One-Click" experience for rendering your video on Google Colab.

## 🎬 Automated Render Cell

Copy and paste the following into a Colab code cell and run it:

```python
# @title 🚀 Start Automated Render
from google.colab import drive
import os
import shutil
import glob

# 1. Mount Google Drive
if not os.path.exists('/content/drive'):
    print("🛰️ Mounting Google Drive...")
    drive.mount('/content/drive')

# --- CONFIGURATION ---
# The main workspace folder in Google Drive:
BASE_DRIVE_PATH = "/content/drive/MyDrive/Counterism_Studio_V4" # @param {type:"string"}
REPO_PATH_LOCAL = "/content/remotion-repo"
PROJECT_PATH_LOCAL = os.path.join(REPO_PATH_LOCAL, "remotion_project_2")
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git" # @param {type:"string"}

# Folder where your scene videos/renders are:
ASSET_SOURCE_DRIVE = f"{BASE_DRIVE_PATH}/renders" # @param {type:"string"}

def setup_and_run():
    # 2. Setup Local Environment
    print("📦 Installing system dependencies...")
    !apt-get install -y ffmpeg --quiet
    !pip install opencv-python --quiet

    print("📦 Initializing local SSD...")
    if os.path.exists(REPO_PATH_LOCAL):
        shutil.rmtree(REPO_PATH_LOCAL)

    print(f"🛰️ Cloning engine from GitHub...")
    !git clone {REPO_URL} {REPO_PATH_LOCAL}

    # 3. AGGRESSIVE ASSET MIRRORING
    print("🚚 Mirroring assets to public root...")
    public_path = os.path.join(PROJECT_PATH_LOCAL, "public")
    os.makedirs(public_path, exist_ok=True)

    asset_count = 0
    # Copy background renders
    if os.path.exists(ASSET_SOURCE_DRIVE):
        for item in os.listdir(ASSET_SOURCE_DRIVE):
            s = os.path.join(ASSET_SOURCE_DRIVE, item)
            if os.path.isfile(s):
                try:
                    shutil.copy2(s, os.path.join(public_path, item))
                    asset_count += 1
                except Exception as e:
                    print(f"⚠️ Could not copy asset {item}: {e}")

    # Filter for font extensions in the Drive project folder
    fonts_to_copy = [f for f in glob.glob(f"{BASE_DRIVE_PATH}/**/*.*", recursive=True)
                     if f.lower().endswith(('.ttf', '.otf', '.woff', '.woff2'))]

    # Also check the specific renders folder
    fonts_to_copy += [os.path.join(ASSET_SOURCE_DRIVE, f) for f in os.listdir(ASSET_SOURCE_DRIVE)
                      if os.path.isfile(os.path.join(ASSET_SOURCE_DRIVE, f)) and f.lower().endswith(('.ttf', '.otf'))]

    copied_fonts = []
    for f in fonts_to_copy:
        fname = os.path.basename(f)
        try:
            shutil.copy2(f, os.path.join(public_path, fname))
            if fname not in copied_fonts:
                copied_fonts.append(fname)
                asset_count += 1
        except Exception as e:
            print(f"⚠️ Could not copy font {fname}: {e}")

    print(f"✅ Mirrored {asset_count} assets to /public")

    # Clean up empty placeholder files
    for f in os.listdir(public_path):
        fpath = os.path.join(public_path, f)
        if os.path.isfile(fpath) and os.path.getsize(fpath) == 0:
            os.remove(fpath)

    # 4. CONFIG SEARCH & DURATION AUTO-FIX
    print("🔍 Searching for configuration in Drive...")
    found_config = None
    config_patterns = [
        f"{BASE_DRIVE_PATH}/master_remotion.json",
        f"{BASE_DRIVE_PATH}/master_render.json",
        f"{BASE_DRIVE_PATH}/**/master_remotion.json",
        f"{BASE_DRIVE_PATH}/**/master_render.json"
    ]

    for pattern in config_patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            found_config = matches[0]
            break

    if found_config:
        print(f"✅ Found config: {found_config}")
        import json
        import re
        import cv2

        def get_video_frame_count(file_path):
            """Returns accurate frame count using ffprobe."""
            import subprocess
            try:
                # ffprobe is more reliable than cv2 for metadata extraction
                cmd = [
                    'ffprobe',
                    '-v', 'error',
                    '-select_streams', 'v:0',
                    '-count_packets',
                    '-show_entries', 'stream=nb_read_packets',
                    '-of', 'csv=p=0',
                    file_path
                ]
                output = subprocess.check_output(cmd).decode('utf-8').strip()
                if output:
                    return int(output)
            except:
                pass

            # Fallback to CV2 if ffprobe fails
            try:
                cap = cv2.VideoCapture(file_path)
                if cap.isOpened():
                    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    cap.release()
                    return frames
            except:
                return None

        try:
            with open(found_config, 'r') as f:
                data = json.load(f)

            # Auto-fix asset names & DURATIONS
            scenes = data.get('scenes', data.get('Scenes', []))
            for scene in scenes:
                src = scene.get('src', '')
                if src and isinstance(src, str) and src.startswith('scene_') and src.endswith('.mp4'):
                    match = re.match(r'scene_(\d+)\.mp4', src)
                    if match:
                        num = match.group(1).zfill(2)
                        src = f"scene_SC_{num}.mp4"
                        scene['src'] = src
                        if 'background' in scene:
                            scene['background']['src'] = src

                # Update duration from actual video file
                asset_path = os.path.join(public_path, src)
                if os.path.exists(asset_path):
                    frames = get_video_frame_count(asset_path)
                    if frames:
                        print(f"⏱️ Updating {src} duration: {scene.get('duration')}f -> {frames}f")
                        scene['duration'] = frames
                        # Sync all text layers to full scene duration
                        layers = scene.get('layers', scene.get('Layers', []))
                        for layer in layers:
                            if layer.get('type') == 'text':
                                layer['duration'] = frames

            target_json = os.path.join(PROJECT_PATH_LOCAL, "src/master_remotion.json")
            with open(target_json, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"✅ Fixed and copied config to {target_json}")
            print("📜 PROCESSED CONFIG SUMMARY:")
            for s in scenes:
                print(f" - {s.get('Id', s.get('id'))}: {s.get('duration')} frames")
        except Exception as e:
            print(f"❌ Error processing config: {e}")
            shutil.copy2(found_config, os.path.join(PROJECT_PATH_LOCAL, "src/master_remotion.json"))
    else:
        print("⚠️ No config found in Drive! Using default from GitHub.")

    # 5. Build and Render
    %cd {PROJECT_PATH_LOCAL}
    print("🟢 Installing dependencies...")
    !rm -f package-lock.json
    !npm install --no-audit --no-fund --quiet

    print("🟢 Ensuring browser...")
    !npm run ensure

    print("🎬 Rendering video...")
    !npm run render

    # 6. Save Result
    if os.path.exists("out/video.mp4"):
        OUTPUT_DRIVE_DIR = os.path.join(BASE_DRIVE_PATH, "out")
        os.makedirs(OUTPUT_DRIVE_DIR, exist_ok=True)
        shutil.copy("out/video.mp4", os.path.join(OUTPUT_DRIVE_DIR, "video.mp4"))
        print(f"\n✅ SUCCESS! Video saved at: {OUTPUT_DRIVE_DIR}/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. See logs above.")

setup_and_run()
```

## 📝 Critical: Font Mismatch?
If you still see "Sohid Osman Hadi" in logs but wanted another font:
1. Open your `master_remotion.json` (or `master_render.json`) in Google Drive.
2. Check the `"banglaFont"` value. **It must be exactly the name of your .ttf file without the extension.**
3. Example: If you have `MyCustomFont.ttf`, the JSON must say `"banglaFont": "MyCustomFont"`.
