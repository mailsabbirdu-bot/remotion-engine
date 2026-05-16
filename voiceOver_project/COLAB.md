# 🎙️ VoiceOver AI - Professional Setup & Run

Paste and run this cell in Google Colab. It will set up the engine and generate your audio scenes automatically.

```python
import os
from google.colab import drive

# --- CONFIGURATION ---
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"
PROJECT_NAME = "voiceOver_project"
# ---------------------

# 1. Mount Drive
if not os.path.exists('/content/drive'):
    print("🛰️ Mounting Google Drive...")
    drive.mount('/content/drive')

# 2. Fresh Clone
print(f"🚀 Initializing VoiceOver Engine...")
os.chdir("/content")
!rm -rf remotion-engine
print("📦 Fetching latest engine from GitHub...")
!git clone {REPO_URL} --quiet
target_dir = f"/content/remotion-engine/{PROJECT_NAME}"

if os.path.exists(target_dir):
    print(f"✅ Project active at: {target_dir}")
    os.chdir(target_dir)

    # 4. Install Dependencies
    print("\n📦 Installing dependencies and browser...")
    !pip install playwright playwright-stealth --quiet
    !playwright install chromium
    !python3 -m playwright install-deps

    # 5. Run
    print("\n" + "="*40)
    print("🎙️ VOICEOVER ENGINE STARTING")
    print("="*40 + "\n")
    # By default, session is stored in Drive/Counterism_Studio_V4/voiceover_session
    # If you need to login, run it once locally or find a way to interact with the browser
    !python main.py
else:
    print("\n❌ Setup failed. Please ensure the project folder is uploaded correctly.")
```

## 🎙️ Note for Novices:
This engine uses your Google AI Studio account.
To make it work without manual login every time:
1. The script saves your session in `Google Drive > Counterism_Studio_V4 > voiceover_session`.
2. Once you are logged in, it will stay logged in as long as the session folder is there.
3. If it asks for login, it means you need to provide a valid session folder or perform a login once.
