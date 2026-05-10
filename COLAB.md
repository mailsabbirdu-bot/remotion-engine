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
# @markdown Path to the folder containing your videos/images (e.g. renders folder):
ASSET_SOURCE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4/renders" # @param {type:"string"}

def setup_and_run():
    # 2. Ensure Project exists in Drive
    if not os.path.exists(PROJECT_PATH_DRIVE):
        print(f"🛰️ Project folder not found in Drive. Creating it...")
        !git clone {REPO_URL} {PROJECT_PATH_DRIVE}
    else:
        if not os.path.exists(os.path.join(PROJECT_PATH_DRIVE, "package.json")):
            print(f"⚠️ Project incomplete in Drive. Repairing...")
            !git clone {REPO_URL} /content/temp_repo
            !cp -rn /content/temp_repo/. {PROJECT_PATH_DRIVE}/
            shutil.rmtree("/content/temp_repo")

    # 3. Sync project to local SSD
    print("📦 Syncing project to local SSD...")
    if os.path.exists(PROJECT_PATH_LOCAL):
        shutil.rmtree(PROJECT_PATH_LOCAL)
    shutil.copytree(PROJECT_PATH_DRIVE, PROJECT_PATH_LOCAL, ignore=shutil.ignore_patterns('node_modules', '.git'))

    # 4. Copy Assets into Public Folder
    # To keep your JSON paths simple, we put them under public/drive/
    print("🚚 Copying assets to public folder...")
    public_drive_path = os.path.join(PROJECT_PATH_LOCAL, "public/drive")
    if os.path.exists(public_drive_path):
        shutil.rmtree(public_drive_path)

    # We want to mirror the path structure from your JSON
    # If JSON has "/drive/Counterism_Studio_V4/renders/scene_1.mp4"
    # We create: public/drive/Counterism_Studio_V4/renders/scene_1.mp4
    target_path = os.path.join(PROJECT_PATH_LOCAL, "public/drive/Counterism_Studio_V4/renders")
    os.makedirs(target_path, exist_ok=True)

    if os.path.exists(ASSET_SOURCE_DRIVE):
        for item in os.listdir(ASSET_SOURCE_DRIVE):
            s = os.path.join(ASSET_SOURCE_DRIVE, item)
            d = os.path.join(target_path, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
        print(f"✅ Assets copied to: {target_path}")
    else:
        print(f"⚠️ Warning: Asset source folder not found at {ASSET_SOURCE_DRIVE}")

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

    # 10. Copy the result back to Google Drive
    if os.path.exists("out/video.mp4"):
        OUTPUT_DRIVE_DIR = os.path.join(PROJECT_PATH_DRIVE, "out")
        os.makedirs(OUTPUT_DRIVE_DIR, exist_ok=True)
        shutil.copy("out/video.mp4", os.path.join(OUTPUT_DRIVE_DIR, "video.mp4"))
        print(f"\n✅ SUCCESS! Video saved at: {OUTPUT_DRIVE_DIR}/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. Check the logs above.")

setup_and_run()
```

## 📝 JSON Path Setup
To match your current JSON, the script puts your files in a folder structure that Remotion can understand.

Use this exact format for your video paths in `master_remotion.json`:
`"src": "/drive/Counterism_Studio_V4/renders/scene_1.mp4"`

**⚠️ Important Checklist:**
- Backgrounds ending in `.mp4` MUST have `"type": "video"`.
- Ensure your font files are in your Drive's `public/fonts/` folder.
