# 🚀 Automated Remotion Engine for Colab

This guide provides a robust "One-Click" experience.

## 🎬 Automated Render Cell

Copy and paste the following into a Colab code cell and run it:

```python
# @title 🚀 Start Automated Render
from google.colab import drive
import os
import shutil

# 1. Mount Google Drive
if not os.path.exists('/content/drive'):
    print("🛰️ Mounting Google Drive...")
    drive.mount('/content/drive')

# --- CONFIGURATION ---
# @markdown ### 📂 Project Path in Google Drive
PROJECT_PATH_DRIVE = "/content/drive/MyDrive/remotion-engine" # @param {type:"string"}
PROJECT_PATH_LOCAL = "/content/remotion-engine"
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git" # @param {type:"string"}

# @markdown ### 📽️ Asset Source Folder (Google Drive)
ASSET_SOURCE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4/renders" # @param {type:"string"}

def setup_and_run():
    # 2. Setup project structure
    if not os.path.exists(PROJECT_PATH_DRIVE):
        print(f"🛰️ Project not found. Cloning...")
        !git clone {REPO_URL} {PROJECT_PATH_DRIVE}

    # 3. Copy to Local SSD
    print("📦 Syncing to local SSD...")
    if os.path.exists(PROJECT_PATH_LOCAL):
        shutil.rmtree(PROJECT_PATH_LOCAL)
    shutil.copytree(PROJECT_PATH_DRIVE, PROJECT_PATH_LOCAL, ignore=shutil.ignore_patterns('node_modules', '.git'))

    # 4. PHYSICAL ASSET COPY (Most reliable)
    # This copies files from your Drive directly into the public/assets folder
    print("🚚 Physically copying assets to public/assets...")
    assets_dir = os.path.join(PROJECT_PATH_LOCAL, "public/assets")
    os.makedirs(assets_dir, exist_ok=True)

    if os.path.exists(ASSET_SOURCE_DRIVE):
        for file in os.listdir(ASSET_SOURCE_DRIVE):
            if file.endswith(('.mp4', '.jpg', '.png', '.wav', '.mp3')):
                shutil.copy2(os.path.join(ASSET_SOURCE_DRIVE, file), os.path.join(assets_dir, file))
        print(f"✅ Assets ready in: {assets_dir}")
        print("Files:", os.listdir(assets_dir))
    else:
        print(f"❌ Error: Asset source {ASSET_SOURCE_DRIVE} not found!")
        return

    # 5. Switch to project directory
    %cd {PROJECT_PATH_LOCAL}

    # 6. Install Node.js
    if shutil.which("node") is None:
        print("🟢 Installing Node.js...")
        !curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - > /dev/null
        !sudo apt-get install -y nodejs > /dev/null

    # 7. Install Dependencies
    print("🟢 Installing NPM packages...")
    if os.path.exists("package-lock.json"):
        os.remove("package-lock.json")
    !npm install --no-audit --no-fund --quiet

    # 8. Setup Browser
    print("🟢 Ensuring browser is ready...")
    !npm run ensure

    # 9. Render the video
    print("🎬 Rendering video...")
    !npm run render

    # 10. Copy result back
    if os.path.exists("out/video.mp4"):
        OUTPUT_DRIVE_DIR = os.path.join(PROJECT_PATH_DRIVE, "out")
        os.makedirs(OUTPUT_DRIVE_DIR, exist_ok=True)
        shutil.copy("out/video.mp4", os.path.join(OUTPUT_DRIVE_DIR, "video.mp4"))
        print(f"\n✅ SUCCESS! Video saved at: {OUTPUT_DRIVE_DIR}/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. Check the logs.")

setup_and_run()
```

## 📝 Note on JSON
Keep your `master_remotion.json` as it is. The engine will automatically find files like `scene_1.mp4` in the `public/assets` folder.
