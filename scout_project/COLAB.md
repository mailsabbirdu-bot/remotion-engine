# 🚀 Scout Project Colab Guide

Run the Scout Engine in Google Colab to automatically scout assets and render individual scenes synced with your audio.

## 📁 Prerequisites (Google Drive)
Ensure your Google Drive has the following folder structure:
- `Counterism_Studio_V4/audio/` -> Put your `SC_01.wav`, `SC_02.wav`, etc. here.
- `Counterism_Studio_V4/renders/` -> Individual scenes will be saved here.
- `Counterism_Studio_V4/manifests/` -> Final `production_plan.json` will be saved here.

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
print("🐍 Installing Python packages (This may take 2-3 minutes)...")
!pip install -r requirements.txt --quiet

# 5. Run the Engine
# Note: Use T4 GPU in Colab for faster filtering
print("\n🎬 STARTING ENGINE...")
!python main.py
```

## 📝 Key Features
- **Intelligent Scouting**: Uses the instructions from `production_plan.json` in the GitHub repo to find the best matching footage from **Pexels** and **Pixabay**.
- **Negative Prompts**: Automatically filters out unwanted content (people, watermarks, etc.) based on scene-specific negative prompts.
- **Audio-First Sync**: Detects your Drive audios (`SC_01.wav`, etc.) and adds **0.5s padding** at both ends.
- **AI Filtering**: Uses CLIP and Semantic Transformers to rank assets by relevance to your text.
- **Scene Isolation**: Renders each scene as an individual `.mp4` file in your Drive `renders/` folder.
