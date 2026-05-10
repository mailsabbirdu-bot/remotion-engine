# 🚀 Running on Google Colab

To run this Remotion project on Google Colab, follow these steps.

## 1. Prepare your Drive
1.  Upload the entire project folder to your Google Drive.
2.  Ensure you have your fonts in `public/fonts/`:
    - `Audiowide-Regular.ttf`
    - `Sohid Osman Hadi.ttf`

## 2. Colab Code Cell
Copy and paste the following into a **single** Colab code cell and run it.

```python
# @title 🎬 Remotion Video Engine Render
from google.colab import drive
import os
import shutil

# 1. Mount Google Drive
if not os.path.exists('/content/drive'):
    drive.mount('/content/drive')

# --- CONFIGURATION ---
# @markdown ### 📂 Project Path in Google Drive
# @markdown Example: /content/drive/MyDrive/remotion-engine
PROJECT_PATH_DRIVE = "/content/drive/MyDrive/remotion-engine" # @param {type:"string"}
PROJECT_PATH_LOCAL = "/content/remotion-engine"

def setup_and_render():
    print("📦 Step 1: Setting up local environment...")

    # Pre-flight check
    if not os.path.exists(PROJECT_PATH_DRIVE):
        print(f"❌ ERROR: Project not found at {PROJECT_PATH_DRIVE}. Please check the path.")
        return

    pkg_path = os.path.join(PROJECT_PATH_DRIVE, "package.json")
    if not os.path.exists(pkg_path):
        print(f"❌ ERROR: package.json not found in {PROJECT_PATH_DRIVE}")
        print("Folder contents:")
        print(os.listdir(PROJECT_PATH_DRIVE))
        return

    # Clean local path
    if os.path.exists(PROJECT_PATH_LOCAL):
        shutil.rmtree(PROJECT_PATH_LOCAL)

    # Copy files
    print(f"🚚 Copying files to local SSD...")
    shutil.copytree(PROJECT_PATH_DRIVE, PROJECT_PATH_LOCAL, ignore=shutil.ignore_patterns('node_modules', '.git'))

    # Change directory using magic command for proper behavior in Colab
    %cd {PROJECT_PATH_LOCAL}

    print(f"📍 Current working directory: {os.getcwd()}")
    if not os.path.exists("package.json"):
        print("❌ ERROR: package.json is missing in local folder after copy!")
        print(os.listdir("."))
        return

    # 3. Install Node.js
    print("🟢 Step 2: Installing Node.js...")
    !curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - > /dev/null
    !sudo apt-get install -y nodejs > /dev/null

    # 4. Install Project Dependencies
    print("🟢 Step 3: Installing NPM packages...")
    !npm install --no-audit --no-fund

    # 5. Ensure Remotion CLI is working
    print("🟢 Step 4: Ensuring browser is ready...")
    !npm run ensure

    # 6. Render the video
    print("🎬 Step 5: Rendering video...")
    !npm run render

    # 7. Copy the result back to Google Drive
    if os.path.exists("out/video.mp4"):
        OUTPUT_DRIVE_DIR = os.path.join(PROJECT_PATH_DRIVE, "out")
        os.makedirs(OUTPUT_DRIVE_DIR, exist_ok=True)
        shutil.copy("out/video.mp4", os.path.join(OUTPUT_DRIVE_DIR, "video.mp4"))
        print(f"\n✅ SUCCESS! Video saved to: {OUTPUT_DRIVE_DIR}/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. video.mp4 not found.")

setup_and_render()
```
