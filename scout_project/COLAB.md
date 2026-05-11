# 🚀 Scout Project Colab Guide

Run the Scout Engine in Google Colab to automatically scout assets and render individual scenes synced with your audio.

## 📁 Prerequisites (Google Drive)
Ensure your Google Drive has the following folder structure:
- `Counterism_Studio_V4/audio/` -> Put your `SC_01.wav`, `SC_02.wav`, etc. here.
- `Counterism_Studio_V4/manifests/` -> Engine will save `production_plan.json` here.
- `Counterism_Studio_V4/renders/` -> Individual scenes will be saved here.

---

## 🎬 Execution Code

Copy and paste the following into a Google Colab code cell:

```python
# @title 🚀 Start Scout Engine
import os
import shutil

# 1. Mount Google Drive
if not os.path.exists('/content/drive'):
    from google.colab import drive
    drive.mount('/content/drive')

# --- CONFIGURATION ---
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"
PROJECT_DIR = "/content/scout-engine"

# 2. Setup Environment
if os.path.exists(PROJECT_DIR):
    shutil.rmtree(PROJECT_DIR)

print("🛰️ Cloning engine...")
!git clone {REPO_URL} {PROJECT_DIR}
%cd {PROJECT_DIR}/scout_project

# 3. Install System Dependencies
print("📦 Installing system dependencies...")
!apt-get install -y ffmpeg libavcodec-extra > /dev/null

# 4. Install Python Dependencies
print("🐍 Installing Python packages (Transformers, Torch, MoviePy)...")
!pip install -r requirements.txt --quiet

# 5. Run the Engine
print("\n🎬 STARTING ENGINE...")
!python main.py
```

## 📝 How it works
1. **Audio Detection**: The engine scans your `Drive > Counterism_Studio_V4 > audio` folder for files named `SC_01.wav`, `SC_02.wav`, etc.
2. **Padding**: It automatically adds **0.5 seconds of silence** at the start and end of each scene.
3. **Plan Update**: A `production_plan.json` is generated in your Drive with exact durations for each scene.
4. **Scouting**: High-quality video or image assets are searched on Pexels/Pixabay based on text prompts.
5. **Individual Renders**: Each scene is rendered as a separate `.mp4` file directly into your `Drive > Counterism_Studio_V4 > renders` folder.
