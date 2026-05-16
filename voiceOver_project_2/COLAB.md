# 🎙️ VoiceOver AI - Coqui XTTS v2 Setup & Run

Paste and run this cell in Google Colab. It will use Coqui XTTS v2 to generate natural-sounding voiceovers with voice cloning.

> **Note:** This script automatically creates a compatible Python 3.10 virtual environment to run Coqui TTS (fixing issues with Colab's default Python 3.12 and recent breaking changes in `transformers`).

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

    # 3. Handle Python Version Compatibility via Venv
    print("\n🔍 Setting up compatible Python 3.10 environment...")
    !sudo apt-get update -y --quiet
    !sudo apt-get install python3.10 python3.10-dev python3.10-venv espeak-ng -y --quiet

    # Create Virtual Environment
    print("🛠️ Creating virtual environment...")
    !python3.10 -m venv /content/tts_venv
    venv_py = "/content/tts_venv/bin/python"
    venv_pip = "/content/tts_venv/bin/pip"

    # 4. Install Python Dependencies in Venv
    print(f"\n📦 Installing dependencies (this may take 2-3 minutes)...")
    # Install specific versions of Torch and Transformers to avoid breaking changes
    !{venv_pip} install torch torchaudio --index-url https://download.pytorch.org/whl/cu121 --quiet
    !{venv_pip} install "numpy<2" "transformers<4.45.0" "setuptools<71.0.0" TTS pydub --quiet

    # 5. Run
    print("\n" + "="*40)
    print("🎙️ VOICEOVER ENGINE STARTING (VENV MODE)")
    print("="*40 + "\n")

    !{venv_py} main.py
else:
    print("\n❌ Setup failed. Please ensure the project folder is uploaded correctly.")
```

## 🎙️ Note for Users:
- This version uses **Coqui XTTS v2** inside a dedicated **Python 3.10 virtual environment**.
- It will automatically use the `clone.wav` file in your `Google Drive > Counterism_Studio_V4 > audio` folder to clone the voice.
- The generated audio files will be saved in the same folder as `SC_01.wav`, `SC_02.wav`, etc.
- Bangla text is supported via a natural Indic accent fallback.
