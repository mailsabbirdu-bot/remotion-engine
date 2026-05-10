# 🚀 One-Click Remotion Engine for Colab

This guide provides a "One-Click" experience. Running the code cell below will automatically setup your environment and render your video.

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

def setup_and_run():
    # 2. Ensure Project exists in Drive
    if not os.path.exists(PROJECT_PATH_DRIVE):
        print(f"🛰️ Project folder not found in Drive. Creating it at {PROJECT_PATH_DRIVE}...")
        !git clone {REPO_URL} {PROJECT_PATH_DRIVE}
    else:
        if not os.path.exists(os.path.join(PROJECT_PATH_DRIVE, "package.json")):
            print(f"⚠️ Project incomplete in Drive. Repairing from repository...")
            !git clone {REPO_URL} /content/temp_repo
            !cp -rn /content/temp_repo/. {PROJECT_PATH_DRIVE}/
            shutil.rmtree("/content/temp_repo")

    # 3. Create necessary subfolders
    os.makedirs(os.path.join(PROJECT_PATH_DRIVE, "public/fonts"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_PATH_DRIVE, "out"), exist_ok=True)

    # 4. Sync to local SSD
    print("📦 Syncing project to local SSD...")
    if os.path.exists(PROJECT_PATH_LOCAL):
        shutil.rmtree(PROJECT_PATH_LOCAL)

    shutil.copytree(PROJECT_PATH_DRIVE, PROJECT_PATH_LOCAL, ignore=shutil.ignore_patterns('node_modules', '.git'))

    # --- IMPORTANT FIX FOR GOOGLE DRIVE PATHS ---
    # Create a symlink so Remotion can serve files from /content/drive
    # If your JSON has "/content/drive/MyDrive/...", it will now work!
    public_content_path = os.path.join(PROJECT_PATH_LOCAL, "public/content")
    if os.path.exists(public_content_path):
        if os.path.islink(public_content_path): os.unlink(public_content_path)
        else: shutil.rmtree(public_content_path)

    os.makedirs(os.path.join(PROJECT_PATH_LOCAL, "public"), exist_ok=True)
    # This creates /content/remotion-engine/public/content which points to /content
    !ln -s /content {PROJECT_PATH_LOCAL}/public/content
    print("🔗 Linked Google Drive to Remotion public folder.")

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

## 📝 Path Configuration in JSON
If your assets are in Google Drive, use their full Colab path in your `master_remotion.json`.
Example: `/content/drive/MyDrive/Counterism_Studio_V4/renders/scene_1.mp4`
The script automatically handles making these files accessible to the Remotion engine.
