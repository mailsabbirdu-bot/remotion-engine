# 🚀 Motion Canvas Sequential Engine (V6)

This cell automates the high-end video production on Google Colab.

```python
# @title 🎬 START MOTION CANVAS RENDER
from google.colab import drive
import os, shutil, subprocess, time

# 1. Mount Drive
if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')

# --- CONFIG ---
BASE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_ROOT = "/content/motion-canvas-production"
PROJECT_DIR = os.path.join(LOCAL_ROOT, "motionCanvas_project")

# IMPORTANT: Ensure your latest code is pushed to this repo
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"

def run_command(cmd, cwd=None):
    print(f"Executing: {cmd}")
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, universal_newlines=True)
    for line in process.stdout:
        print(line, end="")
    process.wait()
    return process.returncode

def setup_and_render():
    print("📦 Installing system dependencies...")
    !apt-get update && apt-get install -y ffmpeg build-essential libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libxshmfence1 libpangocairo-1.0-0 libpango-1.0-0 libxkbcommon0 libatspi-2.0-0 --quiet

    if os.path.exists(LOCAL_ROOT):
        shutil.rmtree(LOCAL_ROOT)

    os.makedirs(LOCAL_ROOT, exist_ok=True)

    print(f"🛰️ Cloning repository...")
    run_command(f"git clone {REPO_URL} {LOCAL_ROOT}")

    # Sync Manifest from Drive
    drive_manifest = os.path.join(BASE_DRIVE, "manifests/motion_canvas.json")
    local_manifest = os.path.join(PROJECT_DIR, "motion_canvas.json")

    if os.path.exists(drive_manifest):
        print("🚚 Syncing manifest from Drive...")
        shutil.copy2(drive_manifest, local_manifest)

    # Mirror Assets (Stock Footage)
    public_path = os.path.join(PROJECT_DIR, "public")
    renders_path = os.path.join(public_path, "renders")
    os.makedirs(renders_path, exist_ok=True)

    drive_renders = os.path.join(BASE_DRIVE, "renders")
    if os.path.exists(drive_renders):
        print("🚚 Linking stock footage from Drive...")
        for f in os.listdir(drive_renders):
            src = os.path.join(drive_renders, f)
            dst = os.path.join(renders_path, f)
            if not os.path.exists(dst) and os.path.isfile(src):
                os.symlink(src, dst)

    print("🟢 Installing Node packages & Playwright...")
    run_command("npm install", cwd=PROJECT_DIR)
    run_command("npx playwright install chromium", cwd=PROJECT_DIR)
    run_command("npx playwright install-deps", cwd=PROJECT_DIR)

    print("🎬 Rendering animation (Headless)...")
    # node render-headless.js
    run_command("node render-headless.js", cwd=PROJECT_DIR)

    # Encode to MP4
    print("🎞️ Encoding video...")
    output_video = os.path.join(PROJECT_DIR, "video.mp4")
    # ffmpeg -y -framerate 30 -i out/%06d.png -c:v libx264 -pix_fmt yuv420p video.mp4
    # Ensure frames exist
    if os.path.exists(os.path.join(PROJECT_DIR, "out")):
        run_command("ffmpeg -y -framerate 30 -i out/%06d.png -c:v libx264 -crf 18 -pix_fmt yuv420p video.mp4", cwd=PROJECT_DIR)

    # Export to Drive
    final_destination = os.path.join(BASE_DRIVE, "out/motion_canvas_final.mp4")
    if os.path.exists(output_video):
        os.makedirs(os.path.dirname(final_destination), exist_ok=True)
        shutil.copy2(output_video, final_destination)
        print(f"✅ SUCCESS! Video saved to {final_destination}")
    else:
        print("❌ Render failed. Check logs above.")

setup_and_render()
```
