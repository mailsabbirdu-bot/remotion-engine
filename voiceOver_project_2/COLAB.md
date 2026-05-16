# 🎙️ VoiceOver AI - Coqui XTTS v2 Setup & Run

Paste and run this cell in Google Colab. It will use Coqui XTTS v2 to generate natural-sounding voiceovers with voice cloning.

```python
import os
from google.colab import drive

# --- CONFIGURATION ---
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"
PROJECT_NAME = "voiceOver_project_2"
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

    # 3. Install System Dependencies
    print("\n📦 Installing system dependencies...")
    !apt-get install -y espeak-ng --quiet

    # 4. Install Python Dependencies
    print("\n📦 Installing Python dependencies (this may take a minute)...")
    !pip install TTS pydub --quiet

    # 5. Run
    print("\n" + "="*40)
    print("🎙️ VOICEOVER ENGINE STARTING (XTTS v2 MODE)")
    print("="*40 + "\n")

    !python main.py
else:
    print("\n❌ Setup failed. Please ensure the project folder is uploaded correctly.")
```

## 🎙️ Note for Users:
- This version uses **Coqui XTTS v2**, which runs locally in Colab (on GPU if available).
- It will automatically use the `clone.wav` file in your `Google Drive > Counterism_Studio_V4 > audio` folder to clone the voice.
- The generated audio files will be saved in the same folder as `SC_01.wav`, `SC_02.wav`, etc.
- Bangla text is supported via a natural Indic accent fallback.
