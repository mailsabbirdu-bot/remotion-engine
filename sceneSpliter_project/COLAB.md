# 🎬 Scene Spliter AI - High-End Setup & Run

Paste and run this cell in Google Colab. It will set up the engine and process your script automatically.

```python
import os
from google.colab import drive

# --- CONFIGURATION ---
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"
PROJECT_NAME = "sceneSpliter_project"
# ---------------------

# 1. Mount Drive
if not os.path.exists('/content/drive'):
    print("🛰️ Mounting Google Drive...")
    drive.mount('/content/drive')

# 2. Fresh Clone
print(f"🚀 Initializing Scene Spliter...")
os.chdir("/content")
!rm -rf remotion-engine
print("📦 Fetching latest engine from GitHub...")
!git clone {REPO_URL} --quiet
target_dir = f"/content/remotion-engine/{PROJECT_NAME}"

if os.path.exists(target_dir):
    print(f"✅ Project active at: {target_dir}")
    os.chdir(target_dir)

    # 4. Install Dependencies
    print("\n📦 Installing dependencies...")
    !pip install google-generativeai --quiet

    # 5. Run
    print("\n" + "="*40)
    print("🎬 SCENE SPLITER AI STARTING")
    print("="*40 + "\n")
    !python main.py
else:
    print("\n❌ Setup failed. Please ensure the project folder is uploaded correctly.")
```
