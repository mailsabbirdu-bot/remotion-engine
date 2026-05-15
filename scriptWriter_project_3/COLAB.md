# 🎬 ScriptWriter AI - Professional Setup & Run

Paste and run this cell in Google Colab. It will find the ScriptWriter project and set everything up automatically.

```python
import os
import subprocess
import sys
from google.colab import drive, files

# --- CONFIGURATION ---
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"
PROJECT_NAME = "scriptWriter_project_3"
REQUIRED_FILES = ["main.py", "requirements.txt", "core/pipeline.py"]
# ---------------------

def is_project_dir(path):
    return all(os.path.exists(os.path.join(path, f)) for f in REQUIRED_FILES)

# 1. Mount Drive (RECOMMENDED for saving scripts)
if not os.path.exists('/content/drive'):
    print("🛰️ Mounting Google Drive...")
    try:
        drive.mount('/content/drive')
    except Exception as e:
        print(f"⚠️ Drive mount failed: {e}")
        print("💡 Continuing in local mode. Your scripts will be deleted when Colab disconnects.")

# 2. Fast Path: Fresh Clone
print(f"🚀 Initializing ScriptWriter...")
os.chdir("/content")
# Remove existing clone to ensure fresh code
!rm -rf remotion-engine
print("📦 Fetching latest engine from GitHub...")
!git clone {REPO_URL} --quiet
target_dir = f"/content/remotion-engine/{PROJECT_NAME}"

if os.path.exists(target_dir):
    print(f"✅ Project active at: {target_dir}")
    os.chdir(target_dir)

    # 4. Install Dependencies
    print("\n📦 Installing dependencies...")
    !pip install -r requirements.txt --quiet
    print("✅ Ready.")

    # 5. Run
    print("\n" + "="*40)
    print("🎬 SCRIPTWRITER AI STARTING")
    print("="*40 + "\n")
    !python main.py
else:
    print("\n❌ Setup failed. Please ensure the project folder is uploaded correctly.")
```
