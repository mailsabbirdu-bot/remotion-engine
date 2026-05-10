# 🚀 Automated Remotion Engine for Colab

This guide provides the most stable "One-Click" experience for rendering videos.

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
# @markdown Path where your scene videos are stored:
ASSET_SOURCE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4/renders" # @param {type:"string"}

def setup_and_run():
    # 2. Sync project to local SSD
    if os.path.exists(PROJECT_PATH_LOCAL):
        shutil.rmtree(PROJECT_PATH_LOCAL)

    if os.path.exists(PROJECT_PATH_DRIVE):
        print("📦 Syncing project to local SSD...")
        shutil.copytree(PROJECT_PATH_DRIVE, PROJECT_PATH_LOCAL, ignore=shutil.ignore_patterns('node_modules', '.git', 'out'))
    else:
        print(f"🛰️ Project folder not found in Drive. Cloning from {REPO_URL}...")
        !git clone {REPO_URL} {PROJECT_PATH_LOCAL}

    # 3. FLAT ASSET COPY (Guarantee 404-free rendering)
    # We copy all media directly into the public/ root folder
    print("🚚 Copying assets to local SSD public folder...")
    public_path = os.path.join(PROJECT_PATH_LOCAL, "public")
    os.makedirs(public_path, exist_ok=True)

    if os.path.exists(ASSET_SOURCE_DRIVE):
        for item in os.listdir(ASSET_SOURCE_DRIVE):
            s = os.path.join(ASSET_SOURCE_DRIVE, item)
            d = os.path.join(public_path, item)
            if os.path.isfile(s) and item.lower().endswith(('.mp4', '.jpg', '.png', '.wav', '.mp3', '.ttf')):
                shutil.copy2(s, d)
        print(f"✅ Assets ready in: {public_path}")
    else:
        print(f"⚠️ Warning: Asset source folder {ASSET_SOURCE_DRIVE} not found!")

    # 4. Switch to project directory
    %cd {PROJECT_PATH_LOCAL}

    # 5. Clean Remotion and Webpack caches
    !rm -rf .remotion node_modules/.cache

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

    # 9. Render the video with CACHE DISABLED for safety
    print("🎬 Rendering video...")
    !npx remotion render src/index.ts Main out/video.mp4 --concurrency=1 --bundle-cache=false

    # 10. Copy result back
    if os.path.exists("out/video.mp4"):
        OUTPUT_DRIVE_DIR = os.path.join(PROJECT_PATH_DRIVE, "out")
        os.makedirs(OUTPUT_DRIVE_DIR, exist_ok=True)
        shutil.copy("out/video.mp4", os.path.join(OUTPUT_DRIVE_DIR, "video.mp4"))
        print(f"\n✅ SUCCESS! Video saved at: {OUTPUT_DRIVE_DIR}/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. Check the logs above.")

setup_and_run()
```

## 📝 Troubleshooting JSON Paths
The engine extracts the filename from any path.
Example: `"src": "/drive/renders/scene_1.mp4"` will correctly find `scene_1.mp4` in the SSD.

**⚠️ Checklist:**
- Backgrounds ending in `.mp4` MUST have `"type": "video"`.
- Ensure font files are in `public/fonts/` in your Drive.
