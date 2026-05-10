# 🚀 One-Click Remotion Engine for Colab

This guide provides a "One-Click" experience. Running the code cell below will automatically:
1. Mount your Google Drive.
2. Setup the project structure if it's missing.
3. Install all necessary software (Node.js, Chrome).
4. Render your video and save it back to your Drive.

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
# @markdown This is where your project files and the final video will live.
PROJECT_PATH_DRIVE = "/content/drive/MyDrive/remotion-engine" # @param {type:"string"}
PROJECT_PATH_LOCAL = "/content/remotion-engine"
# @markdown ### 🔗 Git Repository (Optional)
# @markdown If the project is missing from your Drive, it will be cloned from here.
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git" # @param {type:"string"}

def setup_and_run():
    # 2. Ensure Project exists in Drive
    if not os.path.exists(PROJECT_PATH_DRIVE):
        print(f"🛰️ Project folder not found in Drive. Creating it at {PROJECT_PATH_DRIVE}...")
        !git clone {REPO_URL} {PROJECT_PATH_DRIVE}
    else:
        # Check if project is complete
        if not os.path.exists(os.path.join(PROJECT_PATH_DRIVE, "package.json")):
            print(f"⚠️ Project folder found but seems incomplete (missing package.json).")
            print(f"🔄 Attempting to repair/sync from repository...")
            # Use a temporary clone to fill missing files
            !git clone {REPO_URL} /content/temp_repo
            !cp -rn /content/temp_repo/. {PROJECT_PATH_DRIVE}/
            shutil.rmtree("/content/temp_repo")

    # 3. Create necessary subfolders if missing
    os.makedirs(os.path.join(PROJECT_PATH_DRIVE, "public/fonts"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_PATH_DRIVE, "src/components"), exist_ok=True)
    os.makedirs(os.path.join(PROJECT_PATH_DRIVE, "out"), exist_ok=True)

    # 4. Sync to local SSD (Faster rendering & avoids Drive sync issues)
    print("📦 Syncing project to local SSD...")
    if os.path.exists(PROJECT_PATH_LOCAL):
        shutil.rmtree(PROJECT_PATH_LOCAL)

    # Copy from Drive to Local, preserving your manual edits to master_remotion.json
    shutil.copytree(PROJECT_PATH_DRIVE, PROJECT_PATH_LOCAL, ignore=shutil.ignore_patterns('node_modules', '.git'))

    # 5. Switch to project directory
    %cd {PROJECT_PATH_LOCAL}

    # 6. Install Node.js
    if shutil.which("node") is None:
        print("🟢 Installing Node.js...")
        !curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - > /dev/null
        !sudo apt-get install -y nodejs > /dev/null
    else:
        print("✅ Node.js is already installed.")

    # 7. Install Dependencies
    print("🟢 Installing NPM packages (this may take a minute)...")
    # We delete package-lock.json to ensure a clean install on the local environment
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
        print(f"\n✅ SUCCESS! Your video is ready at: {OUTPUT_DRIVE_DIR}/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. Please check the logs above.")

setup_and_run()
```

## 📝 Usage Tips
1. **Fonts**: Place your custom fonts in the `public/fonts/` folder in your Google Drive.
2. **Configuration**: Edit `src/master_remotion.json` directly in your Google Drive to change the video content.
3. **One-Click**: Once your fonts and JSON are ready, just run the cell above!

## 🛠️ How it works
The script is smart enough to detect if you have the project in your Drive. If you don't, it will automatically download it from GitHub for you. It then moves the files to Colab's high-speed local storage to ensure the render is fast and doesn't crash.
