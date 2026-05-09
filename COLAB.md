# 🚀 Running on Google Colab

To run this Remotion project on Google Colab, follow these steps.

## 1. Prepare your Drive
1.  Upload the entire project folder to your Google Drive.
2.  Ensure you have your fonts in `public/fonts/`:
    - `Audiowide-Regular.ttf`
    - `Sohid Osman Hadi.ttf`

## 2. Colab Code Cell
Copy and paste the following into a **single** Colab code cell and run it.

**Important:** Make sure `PROJECT_PATH_DRIVE` matches the exact folder name in your Google Drive.

```python
# @title 🎬 Remotion Video Engine Render
from google.colab import drive
import os
import shutil
import sys

# 1. Mount Google Drive
if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')

# --- CONFIGURATION ---
# @markdown ### 📂 Project Path in Google Drive
# @markdown Enter the path where you saved this project (e.g., /content/drive/MyDrive/remotion-engine):
PROJECT_PATH_DRIVE = "/content/drive/MyDrive/remotion-engine" # @param {type:"string"}
PROJECT_PATH_LOCAL = "/content/remotion-engine"

def run_render():
    # 2. Setup Project in /content (SSD)
    print("📦 Step 1: Setting up local environment...")
    if os.path.exists(PROJECT_PATH_LOCAL):
        shutil.rmtree(PROJECT_PATH_LOCAL)

    if not os.path.exists(PROJECT_PATH_DRIVE):
        print(f"❌ ERROR: Project not found at {PROJECT_PATH_DRIVE}")
        print("Check your Google Drive and make sure the path is correct.")
        return

    # Check if package.json exists in Drive
    if not os.path.exists(os.path.join(PROJECT_PATH_DRIVE, "package.json")):
        print(f"❌ ERROR: 'package.json' not found in {PROJECT_PATH_DRIVE}")
        print("Did you upload the project correctly? Here is what's in that folder:")
        !ls -F {PROJECT_PATH_DRIVE}
        return

    # Copy from Drive to Local (excluding node_modules)
    os.makedirs(PROJECT_PATH_LOCAL, exist_ok=True)
    print(f"🚚 Copying files from Drive...")
    !cp -r {PROJECT_PATH_DRIVE}/. {PROJECT_PATH_LOCAL}/

    if os.path.exists(f"{PROJECT_PATH_LOCAL}/node_modules"):
        shutil.rmtree(f"{PROJECT_PATH_LOCAL}/node_modules")

    os.chdir(PROJECT_PATH_LOCAL)

    # 3. Install Node.js
    print("🟢 Step 2: Installing Node.js...")
    !curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - > /dev/null
    !sudo apt-get install -y nodejs > /dev/null

    # 4. Install Project Dependencies
    print("🟢 Step 3: Installing NPM packages (this may take a minute)...")
    !npm install --no-audit --no-fund --quiet

    # 5. Install System Dependencies for Remotion
    print("🟢 Step 4: Ensuring browser is ready...")
    !npx remotion browser ensure

    # 6. Render the video
    print("🎬 Step 5: Rendering video (using concurrency=1 for stability)...")
    render_cmd = "!npx remotion render src/index.ts Main out/video.mp4 --concurrency=1"
    !npx remotion render src/index.ts Main out/video.mp4 --concurrency=1

    # 7. Copy the result back to Google Drive
    if os.path.exists("out/video.mp4"):
        OUTPUT_DRIVE_DIR = os.path.join(PROJECT_PATH_DRIVE, "out")
        os.makedirs(OUTPUT_DRIVE_DIR, exist_ok=True)
        shutil.copy("out/video.mp4", os.path.join(OUTPUT_DRIVE_DIR, "video.mp4"))
        print(f"\n✅ SUCCESS! Video saved to: {OUTPUT_DRIVE_DIR}/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. Check the logs above for details.")

run_render()
```

## Troubleshooting
- **package.json not found**: Ensure you didn't put the project inside another subfolder (e.g., `remotion-engine/remotion-engine/package.json`).
- **Font errors**: Ensure your font files are named exactly as `Audiowide-Regular.ttf` and `Sohid Osman Hadi.ttf` and are in the `public/fonts` folder.
- **Drive Timeout**: Sometimes Google Drive takes a moment to sync new files. If a file is missing, wait 30 seconds and try again.
