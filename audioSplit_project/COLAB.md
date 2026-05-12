# ✂️ Audio Split Engine - Colab Execution

**IMPORTANT:**
1. This project uses **Forced Alignment (Wav2Vec2)** for ultra-fast and precise cutting.
2. It is significantly faster and more accurate than transcription-based methods for script-audio alignment.
3. You **MUST** use a **GPU (T4)** runtime in Colab for the best performance.

Copy and run the following cell in your Google Colab notebook to split your `story.wav` into scene-wise audio files.

```python
# @title ✂️ Run Audio Splitter
# 1. Mount Google Drive
from google.colab import drive
import os
import shutil

if not os.path.exists("/content/drive"):
    drive.mount('/content/drive')

# 2. Clone Repository (if not already present)
# Replace REPO_URL with your own fork if needed
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"
PROJECT_DIR = "/content/remotion-engine"

if os.path.exists(PROJECT_DIR):
    shutil.rmtree(PROJECT_DIR)

!git clone {REPO_URL} {PROJECT_DIR}
os.chdir(f"{PROJECT_DIR}/audioSplit_project")

# 3. Install Dependencies
!pip install -r requirements.txt
!apt-get install -y ffmpeg

# 4. Run Engine
!python main.py
```

### Setup Instructions:
1. Ensure you have `story.wav` and `story.txt` in your Google Drive at:
   `My Drive/Counterism_Studio_V4/audio/`
2. `story.txt` should follow the scene-wise format (e.g., `দৃশ্য ১`, `দৃশ্য ২` or `Scene 1`, `Scene 2`).
3. Run the cell above. The engine will automatically transcribe the audio, align it with your script, and save `SC_01.wav`, `SC_02.wav`, etc., back to your Drive.
