# 🚀 Motion Canvas Overlay Engine - Colab Runner (V14)

```python
# @title 🎬 START MOTION CANVAS OVERLAY RENDER
from google.colab import drive
import os, shutil, subprocess, time

# 1. Mount Drive
if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')

# --- CONFIG ---
# 1. Path to your project on Google Drive (where manifest is and where results will go)
BASE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4"

# 2. Local working directory in Colab
LOCAL_ROOT = "/content/motion-canvas-production"

# 3. The name of the project folder to search for
PROJECT_NAME = "motionCan_project"

# 4. Your repository URL.
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
    # Updated library list for Ubuntu 22.04 (Jammy)
    run_command("apt-get update && apt-get install -y ffmpeg build-essential at-spi2-core libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2 --quiet")

    if os.path.exists(LOCAL_ROOT):
        print(f"🧹 Cleaning up {LOCAL_ROOT}...")
        shutil.rmtree(LOCAL_ROOT)

    os.makedirs(LOCAL_ROOT, exist_ok=True)

    if REPO_URL:
        print(f"🛰️ Cloning repository...")
        run_command(f"git clone {REPO_URL} {LOCAL_ROOT}")

    # Search for project directory
    project_dir = ""
    search_paths = [LOCAL_ROOT, os.getcwd(), "/content"]
    for sp in search_paths:
        if not os.path.exists(sp): continue
        for root, dirs, files in os.walk(sp):
            if PROJECT_NAME in dirs:
                project_dir = os.path.abspath(os.path.join(root, PROJECT_NAME))
                break
        if project_dir: break

    if not project_dir:
        print(f"❌ Could not find {PROJECT_NAME} in repository or current environment.")
        return

    print(f"✅ Project directory: {project_dir}")

    # Sync Manifest from Drive
    drive_manifest = os.path.join(BASE_DRIVE, "manifests/motion_canvas.json")
    local_manifest = os.path.join(project_dir, "motion_canvas.json")
    if os.path.exists(drive_manifest):
        print("🚚 Syncing manifest from Drive...")
        shutil.copy2(drive_manifest, local_manifest)
    else:
        print(f"⚠️ Manifest not found on Drive at {drive_manifest}, using local default.")

    print("🟢 Installing Node packages & Playwright...")
    run_command("npm install", cwd=project_dir)
    run_command("npx playwright install chromium", cwd=project_dir)
    run_command("npx playwright install-deps", cwd=project_dir)

    print("🎬 Rendering overlays (Production Mode)...")
    out_dir = os.path.join(project_dir, "out")
    if os.path.exists(out_dir): shutil.rmtree(out_dir)

    # Use 'npm run render' which calls 'node render-headless.js'
    run_command("NODE_OPTIONS='--max-old-space-size=4096' npm run render", cwd=project_dir)

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
            print("❌ No WebM files found in the output directory. Check logs.")
    else:
        print("❌ Render failed. Output directory 'out' does not exist.")

setup_and_render()
```
