# 🚀 Scout Engine for Google Colab

Run the Scout Engine to automatically find visual footage synced with your audio files in Google Drive.

## 🎬 Automated Execution Code

Copy and paste the following into a Google Colab code cell:

```python
# @title 🚀 Run Scout Engine
import os
import shutil

# 1. Mount Google Drive
if not os.path.exists('/content/drive'):
    from google.colab import drive
    drive.mount('/content/drive')

# --- CONFIGURATION ---
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"
WORK_DIR = "/content/scout-engine"

# 2. Prepare Environment
if os.path.exists(WORK_DIR):
    shutil.rmtree(WORK_DIR)

print("🛰️ Cloning latest Scout Engine from GitHub...")
!git clone {REPO_URL} {WORK_DIR}
%cd {WORK_DIR}/scout_project

# 3. System Dependencies
print("📦 Installing system components...")
!apt-get install -y ffmpeg libavcodec-extra > /dev/null

# 4. Python Dependencies
print("🐍 Installing AI models & Python packages (Transformers, Torch, MoviePy)...")
!pip install -r requirements.txt --quiet

# 5. Execute Engine
print("\n🔥 STARTING ENGINE...")
# Recommended: Use T4 GPU runtime in Colab for faster matching
!python main.py
```

## 📁 Required Folder Structure
Your Google Drive must have these folders for the engine to work:
- `Counterism_Studio_V4/audio/` -> Place your `SC_01.wav`, `SC_02.wav`, etc. here.
- `Counterism_Studio_V4/renders/` -> The engine will save the rendered scene videos here.
- `Counterism_Studio_V4/manifests/` -> The engine will save the final generated plan here.

## 📝 Key Details
- **Syncing**: The engine reads visual instructions from `manifests/production_plan.json` in the GitHub repo but uses the audio files in your Drive to determine scene count and timing.
- **Padding**: Every scene automatically gets **0.5s padding** at the beginning and end.
- **Footage**: The engine scouts for both **Video and Images** from Pexels and Pixabay.
- **Negative Prompts**: Scenes are automatically filtered to avoid unwanted content (people, text, watermarks) based on the prompts in the plan.
