# 🚀 Automated Remotion Engine for Colab

This guide provides the absolute most stable "One-Click" experience for rendering your video on Google Colab.

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
PROJECT_PATH_DRIVE = "/content/drive/MyDrive/remotion-engine" # @param {type:"string"}
PROJECT_PATH_LOCAL = "/content/remotion-engine"
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git" # @param {type:"string"}

# Folder in your Drive where your scene videos are stored:
ASSET_SOURCE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4/renders" # @param {type:"string"}

def setup_and_run():
    # 2. Sync project to local SSD
    print("📦 Syncing project to local SSD...")
    if os.path.exists(PROJECT_PATH_LOCAL):
        shutil.rmtree(PROJECT_PATH_LOCAL)

    # REPAIR LOGIC: Check if project is valid in Drive
    drive_is_valid = os.path.exists(PROJECT_PATH_DRIVE) and os.path.exists(os.path.join(PROJECT_PATH_DRIVE, "package.json"))

    if drive_is_valid:
        print(f"✅ Found project in Drive. Mirroring to local SSD...")
        # Ignore node_modules for speed; they will be installed fresh
        shutil.copytree(PROJECT_PATH_DRIVE, PROJECT_PATH_LOCAL, ignore=shutil.ignore_patterns('node_modules', '.git', 'out', 'build'))
    else:
        print(f"🛰️ Project folder not found or invalid in Drive. Cloning fresh from GitHub...")
        !git clone {REPO_URL} {PROJECT_PATH_LOCAL}
        # If it was missing from drive, create a placeholder for results
        if not os.path.exists(PROJECT_PATH_DRIVE):
            os.makedirs(PROJECT_PATH_DRIVE, exist_ok=True)
            print(f"📁 Created project folder in Drive: {PROJECT_PATH_DRIVE}")

    # 3. FORCE CLEAN CACHES
    print("🧹 Cleaning caches...")
    !rm -rf {PROJECT_PATH_LOCAL}/.remotion
    !rm -rf {PROJECT_PATH_LOCAL}/node_modules/.cache

    # 4. FLAT ASSET MIRRORING (Fixes 404s once and for all)
    print("🚚 Mirroring assets to public root...")
    public_path = os.path.join(PROJECT_PATH_LOCAL, "public")
    os.makedirs(public_path, exist_ok=True)

    # Copy background videos/images
    if os.path.exists(ASSET_SOURCE_DRIVE):
        assets = os.listdir(ASSET_SOURCE_DRIVE)
        count = 0
        for item in assets:
            s = os.path.join(ASSET_SOURCE_DRIVE, item)
            if os.path.isfile(s):
                shutil.copy2(s, os.path.join(public_path, item))
                count += 1
        print(f"✅ {count} assets mirrored from {ASSET_SOURCE_DRIVE}")
    else:
        print(f"❌ Error: Asset source {ASSET_SOURCE_DRIVE} not found!")
        return

    # MIRROR FONTS - Search multiple locations and copy to public root
    font_locations = [
        os.path.join(PROJECT_PATH_DRIVE, "public/fonts"),
        os.path.join(PROJECT_PATH_DRIVE, "fonts"),
        os.path.join(PROJECT_PATH_LOCAL, "public/fonts")
    ]

    found_fonts = 0
    for loc in font_locations:
        if os.path.exists(loc):
            for f in os.listdir(loc):
                if f.lower().endswith(('.ttf', '.otf', '.woff', '.woff2')):
                    shutil.copy2(os.path.join(loc, f), os.path.join(public_path, f))
                    found_fonts += 1

    print(f"✅ {found_fonts} fonts ready in public/ root.")
    print("📦 All Files in public/:", os.listdir(public_path))

    # 5. Switch to project directory
    %cd {PROJECT_PATH_LOCAL}

    # 6. Install Node.js if missing
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

    # 9. Render the video with CACHE DISABLED
    print("🎬 Rendering video (bundle-cache=false)...")
    # bundle-cache=false is CRITICAL when assets change frequently
    !npm run render

    # 10. Sync Result to Drive
    if os.path.exists("out/video.mp4"):
        OUTPUT_DRIVE_DIR = os.path.join(PROJECT_PATH_DRIVE, "out")
        os.makedirs(OUTPUT_DRIVE_DIR, exist_ok=True)
        shutil.copy("out/video.mp4", os.path.join(OUTPUT_DRIVE_DIR, "video.mp4"))
        print(f"\n✅ SUCCESS! Video saved at: {OUTPUT_DRIVE_DIR}/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. Check the logs above for red error messages.")

setup_and_run()
```

## 📝 Tips for JSON
- Your `master_remotion.json` is the source of truth.
- For assets, you can use any path (e.g., `/drive/some/folder/video.mp4`).
- The engine will automatically find `video.mp4` in the `public/` folder because it was mirrored there.
