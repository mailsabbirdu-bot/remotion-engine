# 🚀 Motion Canvas One-Cell Colab Runner (V7)

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
# REPLACE WITH YOUR ACTUAL REPOSITORY URL
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"

def run_command(cmd, cwd=None):
    print(f"Executing: {cmd}")
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, universal_newlines=True)
    for line in process.stdout:
        print(line, end="")
    process.wait()
    return process.returncode

def setup_and_render():
    global PROJECT_DIR
    print("📦 Installing system dependencies...")
    # Using subprocess for apt-get to avoid syntax issues in some environments, though ! works in Colab
    run_command("apt-get update && apt-get install -y ffmpeg build-essential --quiet")

    if os.path.exists(LOCAL_ROOT):
        print(f"🧹 Cleaning up {LOCAL_ROOT}...")
        shutil.rmtree(LOCAL_ROOT)

    os.makedirs(LOCAL_ROOT, exist_ok=True)

    print(f"🛰️ Cloning repository...")
    run_command(f"git clone {REPO_URL} {LOCAL_ROOT}")

    if not os.path.exists(PROJECT_DIR):
        print(f"🔍 Searching for motionCanvas_project in {LOCAL_ROOT}...")
        found = False
        for root, dirs, files in os.walk(LOCAL_ROOT):
            if "motionCanvas_project" in dirs:
                PROJECT_DIR = os.path.abspath(os.path.join(root, "motionCanvas_project"))
                print(f"✅ Found project at: {PROJECT_DIR}")
                found = True
                break

        if not found:
            print("❌ Error: Could not find motionCanvas_project directory.")
            # List directory to help debugging
            run_command(f"ls -R {LOCAL_ROOT}")
            return
    else:
        PROJECT_DIR = os.path.abspath(PROJECT_DIR)
        print(f"✅ Project directory confirmed at: {PROJECT_DIR}")

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
    run_command("NODE_OPTIONS='--max-old-space-size=4096' node render-headless.js", cwd=PROJECT_DIR)

    # Encode to MP4
    print("🎞️ Encoding video...")
    output_video = os.path.join(PROJECT_DIR, "video.mp4")
    if os.path.exists(os.path.join(PROJECT_DIR, "out")):
        run_command("ffmpeg -y -framerate 30 -i out/%06d.png -c:v libx264 -crf 18 -pix_fmt yuv420p video.mp4", cwd=PROJECT_DIR)

    # Export to Drive
    final_destination = os.path.join(BASE_DRIVE, "out/motion_canvas_final.mp4")
    if os.path.exists(output_video):
        os.makedirs(os.path.dirname(final_destination), exist_ok=True)
        shutil.copy2(output_video, final_destination)
        print(f"✅ SUCCESS! Video saved to {final_destination}")
    else:
        print("❌ Render failed. Check logs.")

setup_and_render()
```
