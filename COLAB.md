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

# Folder where your scene videos are:
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
        f"{PROJECT_PATH_DRIVE}/master_render.json",
        f"{PROJECT_PATH_DRIVE}/**/master_remotion.json",
        f"{PROJECT_PATH_DRIVE}/**/master_render.json"
    ]

    for pattern in config_patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            found_config = matches[0]
            break

    if found_config:
        print(f"✅ Found config: {found_config}")
        shutil.copy2(found_config, os.path.join(PROJECT_PATH_LOCAL, "src/master_remotion.json"))
        # Print contents for verification
        with open(found_config, 'r') as f:
            print(f"📄 Config content summary: {f.read()[:200]}...")
    else:
        print("⚠️ No config found in Drive! Using default from GitHub.")

    # 4. AGGRESSIVE ASSET MIRRORING
    print("🚚 Mirroring assets to public root...")
    public_path = os.path.join(PROJECT_PATH_LOCAL, "public")
    os.makedirs(public_path, exist_ok=True)

    # Copy background renders
    if os.path.exists(ASSET_SOURCE_DRIVE):
        for item in os.listdir(ASSET_SOURCE_DRIVE):
            s = os.path.join(ASSET_SOURCE_DRIVE, item)
            if os.path.isfile(s):
                shutil.copy2(s, os.path.join(public_path, item))

    # Deep search for ALL fonts in the Drive project folder
    font_files = glob.glob(f"{PROJECT_PATH_DRIVE}/**/*.{os.path.join('*', '*')}", recursive=True)
    # Filter for font extensions
    fonts_to_copy = [f for f in glob.glob(f"{PROJECT_PATH_DRIVE}/**/*.*", recursive=True)
                     if f.lower().endswith(('.ttf', '.otf', '.woff', '.woff2'))]

    # Also check the specific renders folder
    fonts_to_copy += [os.path.join(ASSET_SOURCE_DRIVE, f) for f in os.listdir(ASSET_SOURCE_DRIVE)
                      if os.path.isfile(os.path.join(ASSET_SOURCE_DRIVE, f)) and f.lower().endswith(('.ttf', '.otf'))]

    copied_fonts = []
    for f in fonts_to_copy:
        fname = os.path.basename(f)
        shutil.copy2(f, os.path.join(public_path, fname))
        if fname not in copied_fonts: copied_fonts.append(fname)

    print(f"✅ All mirrored files in /public: {os.listdir(public_path)}")

    # 5. Build and Render
    %cd {PROJECT_PATH_LOCAL}
    print("🟢 Installing dependencies...")
    !rm -f package-lock.json
    !npm install --no-audit --no-fund --quiet

    print("🟢 Ensuring browser...")
    !npm run ensure

    print("🎬 Rendering video...")
    !npm run render

    # 6. Save Result
    if os.path.exists("out/video.mp4"):
        OUTPUT_DRIVE_DIR = os.path.join(PROJECT_PATH_DRIVE, "out")
        os.makedirs(OUTPUT_DRIVE_DIR, exist_ok=True)
        shutil.copy("out/video.mp4", os.path.join(OUTPUT_DRIVE_DIR, "video.mp4"))
        print(f"\n✅ SUCCESS! Video saved at: {OUTPUT_DRIVE_DIR}/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. See logs above.")

setup_and_run()
```

## 📝 Critical: Font Mismatch?
If you still see "Sohid Osman Hadi" in logs but wanted another font:
1. Open your `master_remotion.json` (or `master_render.json`) in Google Drive.
2. Check the `"banglaFont"` value. **It must be exactly the name of your .ttf file without the extension.**
3. Example: If you have `MyCustomFont.ttf`, the JSON must say `"banglaFont": "MyCustomFont"`.
