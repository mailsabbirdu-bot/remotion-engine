# 🚀 MoCanvas Overlay Engine - Colab Runner

```python
# @title 🎬 START MOCANVAS OVERLAY RENDER
from google.colab import drive
import os, shutil, subprocess, time, sys

# 1. Mount Drive
if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')

# --- CONFIG ---
BASE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_ROOT = "/content/mocanvas-production"
PROJECT_NAME = "MoCanvas_project"
# If you have a repo, put it here. Otherwise, it will search locally.
REPO_URL = ""

def print_progress(step, percentage, message=""):
    bar_length = 30
    filled_length = int(bar_length * percentage / 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\rSTEP {step}: [{bar}] {percentage}% | {message}')
    sys.stdout.flush()
    if percentage == 100:
        print()

def run_command(cmd, cwd=None, step_info=None):
    if step_info:
        print(f"\n▶️ {step_info}")

    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, universal_newlines=True)

    for line in process.stdout:
        # Simple heuristic for progress if applicable
        if "Scene" in line and "/" in line:
            try:
                parts = line.split("[")[1].split("]")[0].split("/")
                curr, total = int(parts[0]), int(parts[1])
                print_progress(4, int((curr/total)*100), line.strip())
            except:
                print(f"  {line.strip()}")
        else:
            print(f"  {line.strip()}")

    process.wait()
    return process.returncode

def setup_and_render():
    print("🌟 MoCanvas Engine Initialization...")

    # Step 1: Dependencies
    print_progress(1, 0, "Installing system dependencies")
    run_command("apt-get update && apt-get install -y ffmpeg build-essential fonts-beng-extra --quiet")
    print_progress(1, 100, "System dependencies installed (FFmpeg + Fonts)")

    # Step 2: Project Setup
    print_progress(2, 0, "Setting up project directory")
    if os.path.exists(LOCAL_ROOT):
        shutil.rmtree(LOCAL_ROOT)
    os.makedirs(LOCAL_ROOT, exist_ok=True)

    if REPO_URL:
        run_command(f"git clone {REPO_URL} {LOCAL_ROOT}")

    # Find Project
    project_dir = ""
    search_locations = [
        os.getcwd(),
        LOCAL_ROOT,
        os.path.join(BASE_DRIVE, "projects"),
        "/content",
        "/content/drive/MyDrive" # Scan entire drive as last resort
    ]

    # Priority 1: Direct name match
    for loc in search_locations:
        if not os.path.exists(loc): continue
        if os.path.basename(loc) == PROJECT_NAME:
            project_dir = loc
            break
        potential = os.path.join(loc, PROJECT_NAME)
        if os.path.exists(potential):
            project_dir = potential
            break

    # Priority 2: Marker file match (master_motion.json)
    if not project_dir:
        print_progress(2, 30, "Project folder name not found. Searching for marker file...")
        for root, dirs, files in os.walk("/content"):
            if "master_motion.json" in files and "render-headless.js" in files:
                project_dir = root
                break

    if not project_dir:
        print(f"\n❌ FAILED: Could not find '{PROJECT_NAME}' folder.")
        print(f"💡 TIP: Ensure you have cloned the repository or uploaded the '{PROJECT_NAME}' folder to Colab.")
        return

    print_progress(2, 50, f"Found project at {project_dir}")

    # Sync Manifest
    drive_manifest = os.path.join(BASE_DRIVE, "manifests/master_motion.json")
    local_manifest = os.path.join(project_dir, "master_motion.json")
    if os.path.exists(drive_manifest):
        shutil.copy2(drive_manifest, local_manifest)
        print_progress(2, 80, "Synced manifest from Drive")
    else:
        print_progress(2, 80, "Using local manifest (Drive manifest not found)")

    print_progress(2, 100, "Project setup complete")

    # Step 3: Node Setup
    print_progress(3, 0, "Installing Node modules")
    run_command("npm install", cwd=project_dir)
    print_progress(3, 40, "Installing Playwright")
    run_command("npx playwright install chromium", cwd=project_dir)
    print_progress(3, 70, "Installing Playwright dependencies")
    run_command("npx playwright install-deps", cwd=project_dir)
    print_progress(3, 100, "Node environment ready")

    # Step 4: Render
    print("\n🎬 Starting Production Render...")
    out_dir = os.path.join(project_dir, "out")
    if os.path.exists(out_dir): shutil.rmtree(out_dir)

    render_code = run_command("NODE_OPTIONS='--max-old-space-size=4096' npm run render", cwd=project_dir)

    if render_code != 0:
        print("\n❌ Render failed. Check logs above.")
        return

    # Step 5: Export
    print_progress(5, 0, "Exporting to Drive")
    final_destination_root = os.path.join(BASE_DRIVE, "renders/overlays/motion_canvas")
    os.makedirs(final_destination_root, exist_ok=True)

    if os.path.exists(out_dir):
        files = [f for f in os.listdir(out_dir) if f.endswith(".webm")]
        total_files = len(files)
        for i, f in enumerate(files):
            shutil.copy2(os.path.join(out_dir, f), os.path.join(final_destination_root, f))
            print_progress(5, int(((i+1)/total_files)*100), f"Exported {f}")

        print(f"\n✅ SUCCESS! All overlays saved to: {final_destination_root}")
    else:
        print("\n❌ ERROR: No output found.")

if __name__ == "__main__":
    setup_and_render()
```
