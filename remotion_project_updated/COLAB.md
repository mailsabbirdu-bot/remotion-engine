# 🚀 Automated Remotion AE Machine for Colab

One-cell solution to render your ultra-modern video.

```python
# @title 🎬 Start Automated Render
from google.colab import drive
import os, shutil, glob, json, re

# 1. Mount Drive
if not os.path.exists('/content/drive'): drive.mount('/content/drive')

# --- CONFIG ---
BASE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4"
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"
LOCAL_ROOT = "/content/remotion-repo"
PROJECT_DIR = os.path.join(LOCAL_ROOT, "remotion_project_updated")

def get_video_frame_count(file_path):
    """Returns accurate frame count using ffprobe."""
    import subprocess
    try:
        # Get duration
        cmd_dur = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        duration = float(subprocess.check_output(cmd_dur).decode('utf-8').strip())

        # Get FPS
        cmd_fps = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1', file_path]
        fps_raw = subprocess.check_output(cmd_fps).decode('utf-8').strip()
        if '/' in fps_raw:
            num, den = fps_raw.split('/')
            fps = float(num) / float(den)
        else:
            fps = float(fps_raw)

        return int(round(duration * fps))
    except Exception as e:
        return None

def run():
    print("📦 Setting up environment...")
    # Comprehensive list of dependencies for Headless Chrome on Ubuntu Jammy (22.04)
    !apt-get update && apt-get install -y ffmpeg libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libxshmfence1 libpangocairo-1.0-0 libpango-1.0-0 libxkbcommon0 libatspi-2.0-0 --quiet

    if os.path.exists(LOCAL_ROOT): shutil.rmtree(LOCAL_ROOT)
    print(f"🛰️ Cloning repository...")
    !git clone {REPO_URL} {LOCAL_ROOT}

    # Mirror Assets
    public_path = os.path.join(PROJECT_DIR, "public")
    os.makedirs(public_path, exist_ok=True)

    print("🚚 Mirroring assets to public/ folder...")
    search_paths = [f"{BASE_DRIVE}/renders", BASE_DRIVE]
    asset_count = 0

    # 1. Recursive search for fonts
    font_files = glob.glob(f"{BASE_DRIVE}/**/*.ttf", recursive=True) + \
                 glob.glob(f"{BASE_DRIVE}/**/*.otf", recursive=True)
    for f in font_files:
        try:
            shutil.copy2(f, os.path.join(public_path, os.path.basename(f)))
            asset_count += 1
        except: pass

    # 2. Copy and map videos/images
    for path in search_paths:
        if os.path.exists(path):
            for f in os.listdir(path):
                f_path = os.path.join(path, f)
                if not os.path.isfile(f_path): continue

                f_lower = f.lower()
                # Copy original
                if f_lower.endswith(('.mp4', '.jpg', '.png', '.wav', '.mp3')):
                    try:
                        shutil.copy2(f_path, os.path.join(public_path, f))
                        asset_count += 1

                        # Auto-mapping: scene_SC_01.mp4 -> scene_1.mp4
                        if f_lower.startswith('scene_sc_') and f_lower.endswith('.mp4'):
                            match = re.search(r'scene_sc_(\d+)', f_lower)
                            if match:
                                num = str(int(match.group(1)))
                                clean_name = f"scene_{num}.mp4"
                                shutil.copy2(f_path, os.path.join(public_path, clean_name))
                                asset_count += 1
                    except: pass

    print(f"✅ Mirrored {asset_count} assets to /public")

    # Find and link master_remotion.json with Auto-fix durations
    config_drive = f"{BASE_DRIVE}/master_remotion.json"
    target_json = os.path.join(PROJECT_DIR, "src/master_remotion.json")

    if os.path.exists(config_drive):
        print(f"🔍 Processing config with duration auto-fix...")
        try:
            with open(config_drive, 'r') as f:
                data = json.load(f)

            scenes = data.get('scenes', [])
            for scene in scenes:
                src = scene.get('background', {}).get('src', scene.get('src', ''))
                if not src: continue

                # Try to find the actual file in public folder
                asset_path = os.path.join(public_path, os.path.basename(src))
                if os.path.exists(asset_path) and asset_path.lower().endswith('.mp4'):
                    frames = get_video_frame_count(asset_path)
                    if frames:
                        old_scene_dur = scene.get('duration', frames)
                        print(f"  🎬 {src}: {old_scene_dur} -> {frames} frames")
                        scene['duration'] = frames

                        # Sync layers that were supposed to last the whole scene
                        for layer in scene.get('layers', []):
                            # If layer spans to the end of the scene (with 2 frame buffer), keep it spanning
                            if layer.get('start', 0) + layer.get('duration', 0) >= old_scene_dur - 2:
                                layer['duration'] = max(0, frames - layer.get('start', 0))

            with open(target_json, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Linked and fixed config from Drive")
        except Exception as e:
            print(f"⚠️ Error fixing config: {e}. Using raw copy.")
            shutil.copy2(config_drive, target_json)

    # Install & Render
    %cd {PROJECT_DIR}
    print("🟢 Installing Node packages...")
    # --force to handle any peer dependency issues
    !npm install --no-audit --no-fund --quiet --force

    print("🟢 Ensuring browser...")
    !npm run ensure

    print("🎬 Rendering video (CPU)...")
    os.makedirs("out", exist_ok=True)

    # Use absolute path for public-dir to avoid any relative path issues
    abs_public = os.path.abspath("public")
    !npx remotion render src/index.ts Main out/video.mp4 --public-dir="{abs_public}" --concurrency=1 --bundle-cache=false

    # Save output
    out_local = "out/video.mp4"
    if os.path.exists(out_local):
        os.makedirs(f"{BASE_DRIVE}/out", exist_ok=True)
        shutil.copy2(out_local, f"{BASE_DRIVE}/out/video.mp4")
        print(f"\n✅ SUCCESS! Video saved to {BASE_DRIVE}/out/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. video.mp4 not found in out/.")

run()
```
