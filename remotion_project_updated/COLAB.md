# 🚀 Automated Remotion AE Machine for Colab

One-cell solution to render your ultra-modern video.

```python
# @title 🎬 Start Automated Render
from google.colab import drive
import os, shutil, glob, json

# 1. Mount Drive
if not os.path.exists('/content/drive'): drive.mount('/content/drive')

# --- CONFIG ---
BASE_DRIVE = "/content/drive/MyDrive/Counterism_Studio_V4"
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"
LOCAL_ROOT = "/content/remotion-repo"
PROJECT_DIR = os.path.join(LOCAL_ROOT, "remotion_project_updated")

def run():
    print("📦 Setting up environment...")
    # Install browser dependencies for Remotion
    !apt-get update && apt-get install -y ffmpeg libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2 libxshmfence1 --quiet

    if os.path.exists(LOCAL_ROOT): shutil.rmtree(LOCAL_ROOT)
    print(f"🛰️ Cloning repository...")
    !git clone {REPO_URL} {LOCAL_ROOT}

    # Mirror Assets
    public_path = os.path.join(PROJECT_DIR, "public")
    os.makedirs(public_path, exist_ok=True)

    print("🚚 Mirroring assets to public/ folder...")
    # Copy from renders folder and root project folder
    search_paths = [f"{BASE_DRIVE}/renders", BASE_DRIVE]
    asset_count = 0
    for path in search_paths:
        if os.path.exists(path):
            for f in os.listdir(path):
                if f.lower().endswith(('.mp4', '.jpg', '.png', '.ttf', '.otf', '.wav', '.mp3')):
                    try:
                        shutil.copy2(os.path.join(path, f), os.path.join(public_path, f))
                        asset_count += 1
                    except: pass

    print(f"✅ Mirrored {asset_count} assets.")

    # Find and link master_remotion.json
    config_drive = f"{BASE_DRIVE}/master_remotion.json"
    if os.path.exists(config_drive):
        shutil.copy2(config_drive, os.path.join(PROJECT_DIR, "src/master_remotion.json"))
        print(f"✅ Linked config from Drive")

    # Install & Render
    %cd {PROJECT_DIR}
    print("🟢 Installing Node packages...")
    !npm install --no-audit --no-fund --quiet

    print("🟢 Ensuring browser...")
    !npm run ensure

    print("🎬 Rendering video (CPU)...")
    os.makedirs("out", exist_ok=True)
    !npm run render

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
