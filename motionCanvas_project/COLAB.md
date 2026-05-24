# 🚀 Motion Canvas One-Cell Colab Runner (V2)

```python
# @title 🎬 START MOTION CANVAS RENDER
from google.colab import drive
import os, shutil, subprocess

# 1. Mount Google Drive
if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')

# --- CONFIG ---
BASE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_ROOT = "/content/motion-canvas-repo"
PROJECT_DIR = os.path.join(LOCAL_ROOT, "motionCanvas_project")
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
    !apt-get update && apt-get install -y ffmpeg build-essential --quiet

    if os.path.exists(LOCAL_ROOT):
        shutil.rmtree(LOCAL_ROOT)

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

    print("🟢 Installing Node packages...")
    run_command("npm install", cwd=PROJECT_DIR)

    print("🎬 Rendering frames...")
    # Headless render using the CLI
    run_command("npx @motion-canvas/cli render --output out", cwd=PROJECT_DIR)

    # Convert frames to video
    print("🎞️ Encoding video...")
    output_video = os.path.join(PROJECT_DIR, "video.mp4")
    # Finding the actual frame folder (usually out/main/)
    run_command(f"ffmpeg -y -framerate 30 -i out/main/%06d.png -c:v libx264 -pix_fmt yuv420p {output_video}", cwd=PROJECT_DIR)

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
