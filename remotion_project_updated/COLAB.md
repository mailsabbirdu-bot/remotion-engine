# 🚀 Automated Remotion AE Machine for Colab

One-cell solution to render your ultra-modern video.

```python
# @title 🎬 Start Automated Render
from google.colab import drive
import os, shutil, glob, json, re

# 1. Mount Drive
if not os.path.exists('/content/drive'): drive.mount('/content/drive')

# --- CONFIG ---
BASE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4"
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"
LOCAL_ROOT = "/content/remotion-repo"
PROJECT_DIR = os.path.join(LOCAL_ROOT, "remotion_project_updated")

def run():
    print("📦 Setting up environment...")
    # Comprehensive list of dependencies for Headless Chrome on Ubuntu 22.04
    # We use a robust install command that won't fail if one package is missing
    packages = [
        "ffmpeg", "libnss3", "libatk1.0-0", "libatk-bridge2.0-0", "libcups2",
        "libdrm2", "libxcomposite1", "libxdamage1", "libxrandr2", "libgbm1",
        "libasound2", "libxshmfence1", "libpangocairo-1.0-0", "libpango-1.0-0",
        "libxkbcommon0", "libx11-xcb1"
    ]
    !apt-get update --quiet
    !apt-get install -y {" ".join(packages)} --quiet --fix-missing

    if os.path.exists(LOCAL_ROOT): shutil.rmtree(LOCAL_ROOT)
    print(f"🛰️ Cloning repository...")
    !git clone {REPO_URL} {LOCAL_ROOT}

    # Mirror Assets
    public_path = os.path.join(PROJECT_DIR, "public")
    os.makedirs(public_path, exist_ok=True)

    print("🚚 Mirroring assets to public/ folder...")
    search_paths = [f"{BASE_DRIVE}/renders", BASE_DRIVE]
    asset_count = 0

    # 1. Recursive search for fonts
    font_files = glob.glob(f"{BASE_DRIVE}/**/*.ttf", recursive=True) + \
                 glob.glob(f"{BASE_DRIVE}/**/*.otf", recursive=True)
    for f in font_files:
        try:
            shutil.copy2(f, os.path.join(public_path, os.path.basename(f)))
            asset_count += 1
        except: pass

    # 2. Copy and map videos/images
    for path in search_paths:
        if os.path.exists(path):
            for f in os.listdir(path):
                f_path = os.path.join(path, f)
                if not os.path.isfile(f_path): continue

                f_lower = f.lower()
                if f_lower.endswith(('.mp4', '.jpg', '.png', '.wav', '.mp3')):
                    try:
                        # Copy original
                        shutil.copy2(f_path, os.path.join(public_path, f))
                        asset_count += 1

                        # Auto-mapping: scene_SC_01.mp4 -> scene_1.mp4
                        if f_lower.startswith('scene_sc_') and f_lower.endswith('.mp4'):
                            match = re.search(r'scene_sc_(\d+)', f_lower)
                            if match:
                                num = str(int(match.group(1)))
                                clean_name = f"scene_{num}.mp4"
                                shutil.copy2(f_path, os.path.join(public_path, clean_name))
                                asset_count += 1
                    except: pass

    print(f"✅ Mirrored {asset_count} assets to /public")

    # Find and link master_remotion.json
    config_drive = f"{BASE_DRIVE}/master_remotion.json"
    if os.path.exists(config_drive):
        shutil.copy2(config_drive, os.path.join(PROJECT_DIR, "src/master_remotion.json"))
        print(f"✅ Linked config from Drive")

    # Install & Render
    %cd {PROJECT_DIR}
    print("🟢 Installing Node packages...")
    !npm install --no-audit --no-fund --quiet --force

    print("🟢 Ensuring browser...")
    !npm run ensure

    print("🎬 Rendering video (CPU)...")
    os.makedirs("out", exist_ok=True)

    # Run render with explicit public directory
    !npx remotion render src/index.ts Main out/video.mp4 --public-dir=public --concurrency=1 --bundle-cache=false

    # Save output
    out_local = "out/video.mp4"
    if os.path.exists(out_local):
        os.makedirs(f"{BASE_DRIVE}/out", exist_ok=True)
        shutil.copy2(out_local, f"{BASE_DRIVE}/out/video.mp4")
        print(f"\n✅ SUCCESS! Video saved to {BASE_DRIVE}/out/video.mp4")
    else:
        print("\n❌ ERROR: Render failed. video.mp4 not found in out/.")

run()
```
