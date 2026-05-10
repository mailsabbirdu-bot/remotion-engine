# 🚀 Running on Google Colab

To run this Remotion project on Google Colab, follow these steps.

## ⚠️ Important Setup Requirement
For this to work, you must have the **entire project** (all files and folders) in your Google Drive.
The files should look like this in your Drive folder:
- `src/` (folder)
- `public/` (folder)
- `package.json` (file)
- `tsconfig.json` (file)
- ... (other files)

## Colab Code Cell

Copy and paste the following into a **single** Colab code cell and run it.

```python
# @title 🎬 Remotion Video Engine Render
from google.colab import drive
import os
import shutil

# 1. Mount Google Drive
if not os.path.exists('/content/drive'):
    print("🛰️ Mounting Google Drive...")
    drive.mount('/content/drive')

# --- CONFIGURATION ---
# @markdown ### 📂 Project Path in Google Drive
# @markdown Enter the path where you saved this project (e.g., /content/drive/MyDrive/remotion-engine):
PROJECT_PATH_DRIVE = "/content/drive/MyDrive/remotion-engine" # @param {type:"string"}
PROJECT_PATH_LOCAL = "/content/remotion-engine"

def run_render():
    print("📦 Step 1: Setting up local environment...")

    # 1. Check if Drive folder exists
    if not os.path.exists(PROJECT_PATH_DRIVE):
        print(f"❌ ERROR: Folder not found at {PROJECT_PATH_DRIVE}")
        print("Please check your Google Drive and ensure the path is correct.")
        return

    # 2. Check for package.json (The most important file)
    pkg_path = os.path.join(PROJECT_PATH_DRIVE, "package.json")
    if not os.path.exists(pkg_path):
        print(f"❌ ERROR: 'package.json' is missing in {PROJECT_PATH_DRIVE}")
        print("Here are the files currently in your Drive folder:")
        print(os.listdir(PROJECT_PATH_DRIVE))
        print("\n💡 SOLUTION: Make sure you uploaded ALL files from the project, not just a few folders.")
        return

    # 3. Setup local SSD folder
    if os.path.exists(PROJECT_PATH_LOCAL):
        shutil.rmtree(PROJECT_PATH_LOCAL)

    # 4. Copy everything to SSD
    print(f"🚚 Copying project to local SSD (Faster rendering)...")
    shutil.copytree(PROJECT_PATH_DRIVE, PROJECT_PATH_LOCAL, ignore=shutil.ignore_patterns('node_modules', '.git'))

    # 5. Switch directory using Magic Command
    %cd {PROJECT_PATH_LOCAL}

    # 6. Install Node.js
    print("🟢 Step 2: Installing Node.js...")
    !curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - > /dev/null
    !sudo apt-get install -y nodejs > /dev/null

    # 7. Install Dependencies
    print("🟢 Step 3: Installing NPM packages...")
    !npm install --no-audit --no-fund

    # 8. Setup Browser
    print("🟢 Step 4: Ensuring browser is ready...")
    !npm run ensure

    # 9. Render
    print("🎬 Step 5: Rendering video...")
    !npm run render

    # 10. Copy back to Drive
    if os.path.exists("out/video.mp4"):
        OUTPUT_DRIVE_DIR = os.path.join(PROJECT_PATH_DRIVE, "out")
        os.makedirs(OUTPUT_DRIVE_DIR, exist_ok=True)
        shutil.copy("out/video.mp4", os.path.join(OUTPUT_DRIVE_DIR, "video.mp4"))
        print(f"\n✅ SUCCESS! Video saved to: {OUTPUT_DRIVE_DIR}/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. Check logs above.")

run_render()
```

## Why copy to SSD?
Google Drive is slow and doesn't support complex file operations needed by `npm`. We copy the project to `/content/remotion-engine` (Colab's local high-speed SSD) to ensure stability and speed.
