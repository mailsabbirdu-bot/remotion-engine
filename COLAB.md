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
# The folder where your project files (master_remotion.json, fonts, etc) are stored:
PROJECT_PATH_DRIVE = "/content/drive/MyDrive/remotion-engine" # @param {type:"string"}
PROJECT_PATH_LOCAL = "/content/remotion-engine"
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git" # @param {type:"string"}

# Folder in your Drive where your scene videos are stored:
ASSET_SOURCE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4/renders" # @param {type:"string"}

def setup_and_run():
    # 2. Setup Local Project
    print("📦 Setting up local environment...")
    if os.path.exists(PROJECT_PATH_LOCAL):
        shutil.rmtree(PROJECT_PATH_LOCAL)

    # Always clone fresh from GitHub to get the latest engine code
    print(f"🛰️ Cloning engine from GitHub...")
    !git clone {REPO_URL} {PROJECT_PATH_LOCAL}

    # 3. OVERWRITE WITH DRIVE CONFIG (Crucial Fix)
    # We look for master_remotion.json or master_render.json in your Drive project folder
    config_names = ["master_remotion.json", "master_render.json"]
    found_config = False
    for name in config_names:
        drive_config = os.path.join(PROJECT_PATH_DRIVE, name)
        if os.path.exists(drive_config):
            print(f"✅ Found config: {name} in Drive. Applying...")
            shutil.copy2(drive_config, os.path.join(PROJECT_PATH_LOCAL, "src/master_remotion.json"))
            found_config = True
            break

    if not found_config:
        print("⚠️ No config found in Drive! Using default from repository.")

    # 4. FLAT ASSET MIRRORING
    print("🚚 Mirroring assets to public root...")
    public_path = os.path.join(PROJECT_PATH_LOCAL, "public")
    os.makedirs(public_path, exist_ok=True)

    # Copy background videos/images
    if os.path.exists(ASSET_SOURCE_DRIVE):
        assets = os.listdir(ASSET_SOURCE_DRIVE)
        for item in assets:
            s = os.path.join(ASSET_SOURCE_DRIVE, item)
            if os.path.isfile(s):
                shutil.copy2(s, os.path.join(public_path, item))

    # MIRROR FONTS - Specifically look in Drive project/fonts and root fonts
    font_locations = [
        os.path.join(PROJECT_PATH_DRIVE, "public/fonts"),
        os.path.join(PROJECT_PATH_DRIVE, "fonts"),
        os.path.join(PROJECT_PATH_DRIVE, "public"), # Root of public
        ASSET_SOURCE_DRIVE
    ]

    found_fonts = []
    for loc in font_locations:
        if os.path.exists(loc):
            for f in os.listdir(loc):
                if f.lower().endswith(('.ttf', '.otf', '.woff', '.woff2')):
                    shutil.copy2(os.path.join(loc, f), os.path.join(public_path, f))
                    if f not in found_fonts: found_fonts.append(f)

    print(f"✅ Fonts ready: {found_fonts}")

    # 5. Switch to project directory
    %cd {PROJECT_PATH_LOCAL}

    # 6. Install NPM packages
    print("🟢 Installing dependencies (this may take a minute)...")
    if os.path.exists("package-lock.json"):
        os.remove("package-lock.json")
    !npm install --no-audit --no-fund --quiet

    # 7. Setup Browser
    !npm run ensure

    # 8. Render
    print("🎬 Rendering video...")
    !npm run render

    # 9. Sync Result back to Drive
    if os.path.exists("out/video.mp4"):
        OUTPUT_DRIVE_DIR = os.path.join(PROJECT_PATH_DRIVE, "out")
        os.makedirs(OUTPUT_DRIVE_DIR, exist_ok=True)
        shutil.copy("out/video.mp4", os.path.join(OUTPUT_DRIVE_DIR, "video.mp4"))
        print(f"\n✅ SUCCESS! Video saved at: {OUTPUT_DRIVE_DIR}/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. See logs above.")

setup_and_run()
```

## 📝 Troubleshooting Fonts
- **Important:** Ensure your `.ttf` filename exactly matches the `banglaFont` or `englishFont` value in your JSON.
- If your font file is `MyBanglaFont.ttf`, your JSON should say: `"banglaFont": "MyBanglaFont"`.
- If you have a file named `master_render.json` in your Drive, it will automatically be used.
