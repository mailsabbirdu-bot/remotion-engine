# 🚀 Automated Remotion Engine for Colab

This guide provides the absolute most stable "One-Click" experience for rendering your video on Google Colab.

## 🎬 Automated Render Cell

Copy and paste the following into a Colab code cell and run it:

```python
# @title 🚀 Start Automated Render
from google.colab import drive
import os
import shutil
import glob

# 1. Mount Google Drive
if not os.path.exists('/content/drive'):
    print("🛰️ Mounting Google Drive...")
    drive.mount('/content/drive')

# --- CONFIGURATION ---
# The folder where your project is stored in Drive:
PROJECT_PATH_DRIVE = "/content/drive/MyDrive/remotion-engine" # @param {type:"string"}
PROJECT_PATH_LOCAL = "/content/remotion-engine"
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git" # @param {type:"string"}

# Folder where your scene videos are (e.g., from Scout Project):
ASSET_SOURCE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4/renders" # @param {type:"string"}

def setup_and_run():
    # 2. Setup Local Environment
    print("📦 Initializing local SSD...")
    if os.path.exists(PROJECT_PATH_LOCAL):
        shutil.rmtree(PROJECT_PATH_LOCAL)

    print(f"🛰️ Cloning engine from GitHub...")
    !git clone {REPO_URL} {PROJECT_PATH_LOCAL}

    # 3. DEEP CONFIG SEARCH (Find master_remotion.json anywhere in your Drive project)
    print("🔍 Searching for configuration in Drive...")
    found_config = None
    config_patterns = [
        f"{PROJECT_PATH_DRIVE}/master_remotion.json",
        f"{PROJECT_PATH_DRIVE}/src/master_remotion.json",
        f"{PROJECT_PATH_DRIVE}/master_render.json",
        f"{PROJECT_PATH_DRIVE}/**/master_remotion.json",
        f"{PROJECT_PATH_DRIVE}/**/master_render.json"
    ]

    for pattern in config_patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            # Sort by depth to prefer root config
            matches.sort(key=lambda x: x.count('/'))
            found_config = matches[0]
            break

    if found_config:
        print(f"✅ Found config: {found_config}")
        shutil.copy2(found_config, os.path.join(PROJECT_PATH_LOCAL, "src/master_remotion.json"))
    else:
        print("⚠️ No config found in Drive! Using default from GitHub.")

    # 4. AGGRESSIVE ASSET MIRRORING (Guaranteed 404 Fix)
    print("🚚 Mirroring assets to public root...")
    public_path = os.path.join(PROJECT_PATH_LOCAL, "public")
    os.makedirs(public_path, exist_ok=True)

    # Copy background renders from the specified source
    if os.path.exists(ASSET_SOURCE_DRIVE):
        print(f"📁 Copying assets from: {ASSET_SOURCE_DRIVE}")
        for item in os.listdir(ASSET_SOURCE_DRIVE):
            s = os.path.join(ASSET_SOURCE_DRIVE, item)
            if os.path.isfile(s):
                shutil.copy2(s, os.path.join(public_path, item))
    else:
        print(f"⚠️ ASSET_SOURCE_DRIVE not found: {ASSET_SOURCE_DRIVE}")

    # Deep search for ALL fonts and media in the Drive project folder to be safe
    print("🔍 Scanning Drive project for additional media/fonts...")
    extra_assets = glob.glob(f"{PROJECT_PATH_DRIVE}/**/*.*", recursive=True)
    extensions_to_mirror = ('.ttf', '.otf', '.woff', '.woff2', '.mp4', '.mp3', '.wav', '.png', '.jpg', '.jpeg')

    mirrored_count = 0
    for f in extra_assets:
        if f.lower().endswith(extensions_to_mirror):
            fname = os.path.basename(f)
            dest = os.path.join(public_path, fname)
            if not os.path.exists(dest):
                shutil.copy2(f, dest)
                mirrored_count += 1

    print(f"✅ Mirrored {mirrored_count} additional assets.")
    print(f"📦 Total files in /public: {len(os.listdir(public_path))}")

    # 5. Build and Render
    %cd {PROJECT_PATH_LOCAL}
    print("🟢 Installing dependencies...")
    !rm -f package-lock.json
    !npm install --no-audit --no-fund --quiet

    print("🟢 Ensuring browser...")
    !npm run ensure

    print("🎬 Rendering video...")
    # bundle-cache=false is critical when assets are mirrored at runtime
    !npm run render -- --bundle-cache=false

    # 6. Save Result
    if os.path.exists("out/video.mp4"):
        OUTPUT_DRIVE_DIR = os.path.join(PROJECT_PATH_DRIVE, "out")
        os.makedirs(OUTPUT_DRIVE_DIR, exist_ok=True)
        shutil.copy("out/video.mp4", os.path.join(OUTPUT_DRIVE_DIR, "video.mp4"))
        print(f"\n✅ SUCCESS! Video saved at: {OUTPUT_DRIVE_DIR}/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. Check the logs above for '404' or 'Module not found' errors.")

setup_and_run()
```

## 📝 Critical: Font Mismatch?
If you still see "Sohid Osman Hadi" in logs but wanted another font:
1. Open your `master_remotion.json` in Google Drive.
2. Check the `"banglaFont"` and `"englishFont"` values. **They must be exactly the name of your .ttf file without the extension.**
3. Example: If you have `MyCustomFont.ttf`, the JSON must say `"banglaFont": "MyCustomFont"`.
