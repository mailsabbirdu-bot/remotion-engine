# 🎥 JSON Maker V2 - All-Inclusive Setup

Paste and run this cell in Google Colab. It will automatically clone the repository, install Playwright with all necessary system dependencies, and execute the engine.

```python
import os
import subprocess
import sys
from google.colab import drive

# --- CONFIGURATION ---
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"
PROJECT_NAME = "jsonMaker_project_2"
# ---------------------

# 1. Mount Google Drive
if not os.path.exists('/content/drive'):
    print("🛰️ Mounting Google Drive...")
    drive.mount('/content/drive')

# 2. Setup Repository
print(f"🚀 Initializing {PROJECT_NAME}...")
os.chdir("/content")
!rm -rf remotion-engine
print("📦 Fetching latest engine from GitHub...")
!git clone {REPO_URL} --quiet

target_dir = f"/content/remotion-engine/{PROJECT_NAME}"

if os.path.exists(target_dir):
    os.chdir(target_dir)

    # 3. Install Dependencies
    print("📦 Installing Python dependencies...")
    !pip install playwright playwright-stealth pydub --quiet

    print("🌐 Installing Playwright Browser & System Deps...")
    !playwright install chromium
    !python3 -m playwright install-deps

    print("✅ Setup Complete.")

    # 4. Run the Engine
    print("\n" + "="*40)
    print("🎬 JSON MAKER V2 STARTING")
    print("="*40 + "\n")
    !python3 main.py
else:
    print(f"\n❌ Error: Could not find project folder '{PROJECT_NAME}' in the repository.")
```

### Important Notes:
1. **Google Drive**: Ensure your `jsonPrep.txt` and `story.txt` are located in `MyDrive/Counterism_Studio_V4/audio/`.
2. **First Run**: The first time you run this, you may need to handle the Gemini login. It is recommended to run in a local environment first to save the session, or use a persistent session folder.
