# 🎙️ VoiceOver AI - Coqui XTTS v2 Setup & Run

Paste and run this cell in Google Colab. It will use Coqui XTTS v2 to generate natural-sounding voiceovers with voice cloning.

> **Note:** This script automatically handles Python version compatibility for Coqui TTS (it will use Python 3.10 if 3.12 is detected).

```python
import os
import sys
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

    # 3. Handle Python Version Compatibility
    print("\n🔍 Checking Python version...")
    py_version = sys.version_info
    py_cmd = "python3"

    if py_version.major == 3 and py_version.minor >= 12:
        print("⚠️ Python 3.12+ detected. Coqui TTS requires Python < 3.12.")
        print("🛠️ Installing Python 3.10 and dependencies...")
        !sudo apt-get update -y --quiet
        !sudo apt-get install python3.10 python3.10-dev python3.10-distutils espeak-ng -y --quiet
        !curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
        py_cmd = "python3.10"
    else:
        print(f"✅ Python {py_version.major}.{py_version.minor} is compatible.")
        !apt-get install -y espeak-ng --quiet

    # 4. Install Python Dependencies
    print(f"\n📦 Installing Python dependencies using {py_cmd} (this may take a minute)...")
    !{py_cmd} -m pip install TTS pydub --quiet

    # 5. Run
    print("\n" + "="*40)
    print(f"🎙️ VOICEOVER ENGINE STARTING ({py_cmd} mode)")
    print("="*40 + "\n")

    !{py_cmd} main.py
else:
    print("\n❌ Setup failed. Please ensure the project folder is uploaded correctly.")
```

## 🎙️ Note for Users:
- This version uses **Coqui XTTS v2**, which runs locally in Colab (on GPU if available).
- It will automatically use the `clone.wav` file in your `Google Drive > Counterism_Studio_V4 > audio` folder to clone the voice.
- The generated audio files will be saved in the same folder as `SC_01.wav`, `SC_02.wav`, etc.
- Bangla text is supported via a natural Indic accent fallback.
