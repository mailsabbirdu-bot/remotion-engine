# Scene Spliter Project - Google Colab Setup

Run the following code in a single cell in Google Colab to set up and run the Scene Spliter engine.

```python
# ==========================================
# 🎬 SCENE SPLITER ENGINE - ONE-CLICK SETUP
# ==========================================

import os
import shutil

# 1. Mount Google Drive
from google.colab import drive
if not os.path.exists("/content/drive"):
    drive.mount('/content/drive')

# 2. Project Path
PROJECT_DIR = "sceneSpliter_project"

# 3. Install Dependencies
!pip install playwright playwright-stealth google-generativeai
!playwright install chromium
!python3 -m playwright install-deps

# 4. Clone/Set up the project (Assuming files are already there or need to be moved)
# If you are running this from the repo root:
if not os.path.exists(PROJECT_DIR):
    print(f"❌ {PROJECT_DIR} not found in current directory.")
else:
    os.chdir(PROJECT_DIR)

    # 5. Execute the Engine
    !python3 main.py
```

### Manual Mode (Local)
If you are running locally, ensure you have a `Counterism_Studio_V4/audio/script.txt` file and run:
```bash
pip install -r requirements.txt
playwright install chromium
python main.py
```
