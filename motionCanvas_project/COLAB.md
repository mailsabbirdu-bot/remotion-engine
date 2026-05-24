# 🚀 Motion Canvas Overlay Engine - Colab Runner (V11)

```python
# @title 🎬 START MOTION CANVAS OVERLAY RENDER
from google.colab import drive
import os, shutil, subprocess, time

# 1. Mount Drive
if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')

# --- CONFIG ---
BASE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_ROOT = "/content/motion-canvas-production"
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
    global PROJECT_DIR
    print("📦 Installing system dependencies...")
    run_command("apt-get update && apt-get install -y ffmpeg build-essential --quiet")

    if os.path.exists(LOCAL_ROOT):
        print(f"🧹 Cleaning up {LOCAL_ROOT}...")
        shutil.rmtree(LOCAL_ROOT)

    os.makedirs(LOCAL_ROOT, exist_ok=True)

    print(f"🛰️ Cloning repository...")
    run_command(f"git clone {REPO_URL} {LOCAL_ROOT}")

    if not os.path.exists(PROJECT_DIR):
        print(f"🔍 Searching for project directory...")
        for root, dirs, files in os.walk(LOCAL_ROOT):
            if "motionCanvas_project" in dirs:
                PROJECT_DIR = os.path.abspath(os.path.join(root, "motionCanvas_project"))
                break

    print(f"✅ Project directory: {PROJECT_DIR}")

    # Sync Manifest from Drive
    drive_manifest = os.path.join(BASE_DRIVE, "manifests/motion_canvas.json")
    local_manifest = os.path.join(PROJECT_DIR, "motion_canvas.json")
    if os.path.exists(drive_manifest):
        print("🚚 Syncing manifest from Drive...")
        shutil.copy2(drive_manifest, local_manifest)

    print("🟢 Installing Node packages & Playwright...")
    run_command("npm install", cwd=PROJECT_DIR)
    run_command("npx playwright install chromium", cwd=PROJECT_DIR)
    run_command("npx playwright install-deps", cwd=PROJECT_DIR)

    print("🎬 Rendering overlays (Production Mode)...")
    out_dir = os.path.join(PROJECT_DIR, "out")
    if os.path.exists(out_dir): shutil.rmtree(out_dir)

    run_command("NODE_OPTIONS='--max-old-space-size=4096' node render-headless.js", cwd=PROJECT_DIR)

    # Export to Drive
    final_destination_root = os.path.join(BASE_DRIVE, "renders/overlays/motion_canvas")
    os.makedirs(final_destination_root, exist_ok=True)

    if os.path.exists(out_dir):
        print(f"🚚 Exporting rendered scenes to Drive...")
        copied_count = 0
        for f in os.listdir(out_dir):
            if f.endswith(".webm"):
                src = os.path.join(out_dir, f)
                dst = os.path.join(final_destination_root, f)
                shutil.copy2(src, dst)
                print(f"  ✅ Exported: {f}")
                copied_count += 1

        if copied_count > 0:
            print(f"🏁 SUCCESS! {copied_count} overlays saved to {final_destination_root}")
        else:
            print("❌ No WebM files found in the output directory. Check FFmpeg logs.")
    else:
        print("❌ Render failed. Check logs.")

setup_and_render()
```
