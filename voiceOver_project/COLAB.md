# 🎙️ VoiceOver AI - API Setup & Run (No Login Needed)

Paste and run this cell in Google Colab. It will use the Gemini API to generate your audio scenes automatically.

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
    print("\n📦 Installing dependencies...")
    !pip install google-genai --quiet

    # 5. Run
    print("\n" + "="*40)
    print("🎙️ VOICEOVER ENGINE STARTING (API MODE)")
    print("="*40 + "\n")

    # It will automatically use the API Key from your config
    !python main.py
else:
    print("\n❌ Setup failed. Please ensure the project folder is uploaded correctly.")
```

## 🎙️ Note for Users:
This version uses the **Gemini API** directly, so you **DO NOT NEED TO LOGIN** via a browser!
It is much faster and more reliable.

The audio files will be saved in your `Google Drive > Counterism_Studio_V4 > audio` folder.
