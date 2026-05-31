# 🎥 Duration for Remotion - Colab Setup

Paste and run this cell in Google Colab to update your `guideline_prompt.txt` with video durations.

```python
import os
from google.colab import drive

# --- CONFIGURATION ---
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"
PROJECT_NAME = "duration_forRemotion"
# ---------------------

# 1. Mount Google Drive
if not os.path.exists('/content/drive'):
    print("🛰️ Mounting Google Drive...")
    drive.mount('/content/drive')

# 2. Setup Repository
print(f"🚀 Initializing {PROJECT_NAME}...")
os.chdir("/content")
if os.path.exists("remotion-engine"):
    !rm -rf remotion-engine

print("📦 Fetching latest engine from GitHub...")
!git clone {REPO_URL} --quiet

target_dir = f"/content/remotion-engine/{PROJECT_NAME}"

if os.path.exists(target_dir):
    os.chdir(target_dir)

    # 3. Install Dependencies
    print("📦 Installing dependencies...")
    !pip install opencv-python --quiet

    # 4. Run the Engine
    print("\n" + "="*40)
    print("🎬 DURATION ENGINE STARTING")
    print("="*40 + "\n")
    !python3 main.py
else:
    print(f"\n❌ Error: Could not find project folder '{PROJECT_NAME}' in the repository.")
```
