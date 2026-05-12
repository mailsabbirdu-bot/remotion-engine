# 🎬 ScriptWriter AI - Professional Setup & Run

Paste and run this cell in Google Colab. It will find the ScriptWriter project and set everything up automatically.

```python
import os
import subprocess
import sys
from google.colab import drive, files

# --- CONFIGURATION ---
REPO_URL = "https://github.com/mailsabbirdu-bot/remotion-engine.git"
PROJECT_NAME = "scriptWriter_project"
REQUIRED_FILES = ["main.py", "requirements.txt", "core/pipeline.py"]
# ---------------------

def is_project_dir(path):
    return all(os.path.exists(os.path.join(path, f)) for f in REQUIRED_FILES)

def locate_project():
    print(f"🔍 Searching for '{PROJECT_NAME}'...")

    # Priority 1: Current directory
    if is_project_dir(os.getcwd()):
        return os.getcwd()

    # Priority 2: /content/PROJECT_NAME
    colab_path = f"/content/{PROJECT_NAME}"
    if os.path.exists(colab_path) and is_project_dir(colab_path):
        return colab_path

    # Priority 3: Deep search in /content (handles clones and subdirs)
    print("📂 Searching local storage...")
    for root, dirs, _ in os.walk("/content"):
        if PROJECT_NAME in dirs:
            path = os.path.join(root, PROJECT_NAME)
            if is_project_dir(path): return path
        # Check if the current root itself is the project
        if is_project_dir(root): return root

    # Priority 4: Google Drive
    if os.path.exists("/content/drive/MyDrive"):
        print("📂 Searching Google Drive (this may take a minute)...")
        # Optimization: Check MyDrive root first
        drive_root = "/content/drive/MyDrive"
        for item in os.listdir(drive_root):
            path = os.path.join(drive_root, item)
            if os.path.isdir(path) and (item == PROJECT_NAME or is_project_dir(path)):
                if is_project_dir(path): return path

        # Deeper search
        for root, dirs, _ in os.walk(drive_root):
            if PROJECT_NAME in dirs:
                path = os.path.join(root, PROJECT_NAME)
                if is_project_dir(path): return path
    return None

# 1. Mount Drive
if not os.path.exists('/content/drive'):
    try: drive.mount('/content/drive')
    except: print("⚠️ Drive mount skipped.")

# 2. Find Project
target_dir = locate_project()

# 3. Fallback: Git Clone or Upload
if not target_dir:
    print("\n❌ Project folder not found!")
    choice = input("Would you like to: \n(1) Auto-Clone from GitHub \n(2) Upload ZIP \n[Enter 1 or 2]: ")

    if choice == "1":
        os.chdir("/content")
        !git clone {REPO_URL}
        target_dir = locate_project()
    elif choice == "2":
        print("Please upload your project ZIP file...")
        uploaded = files.upload()
        for fn in uploaded.keys():
            if fn.endswith('.zip'):
                !unzip -q {fn} -d /content/uploaded_project
                target_dir = locate_project()

if target_dir:
    print(f"✅ Project active at: {target_dir}")
    os.chdir(target_dir)

    # 4. Install Dependencies
    print("\n📦 Installing dependencies...")
    !pip install -r requirements.txt --quiet
    print("✅ Ready.")

    # 5. Run
    print("\n" + "="*40)
    print("🎬 SCRIPTWRITER AI STARTING")
    print("="*40 + "\n")
    !python main.py
else:
    print("\n❌ Setup failed. Please ensure the project folder is uploaded correctly.")
```
