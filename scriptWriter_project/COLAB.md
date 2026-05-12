# 🎬 Smart ScriptWriter AI - Setup & Run

Paste and run this cell in Google Colab. It will find the project and set everything up automatically.

```python
import os
import subprocess
import sys
from google.colab import drive, files

# --- CONFIGURATION ---
PROJECT_NAME = "scriptWriter_project"
CORE_FILE = "core/pipeline.py"
# ---------------------

def locate_project():
    print(f"🔍 Searching for '{PROJECT_NAME}'...")

    # 1. Check current directory
    if os.path.exists(CORE_FILE):
        return os.getcwd()

    # 2. Check /content/PROJECT_NAME
    if os.path.exists(f"/content/{PROJECT_NAME}/{CORE_FILE}"):
        return f"/content/{PROJECT_NAME}"

    # 3. Check inside any folder in /content (e.g. if repo was cloned)
    for item in os.listdir("/content"):
        potential = os.path.join("/content", item, PROJECT_NAME)
        if os.path.isdir(potential) and os.path.exists(os.path.join(potential, CORE_FILE)):
            return potential
        # Maybe the repo IS the project (no subfolder)
        repo_path = os.path.join("/content", item)
        if os.path.isdir(repo_path) and os.path.exists(os.path.join(repo_path, CORE_FILE)):
            return repo_path

    # 4. Check Google Drive
    if os.path.exists("/content/drive/MyDrive"):
        print("📂 Searching Google Drive (this may take a minute)...")
        for root, dirs, files_list in os.walk("/content/drive/MyDrive"):
            if PROJECT_NAME in dirs:
                path = os.path.join(root, PROJECT_NAME)
                if os.path.exists(os.path.join(path, CORE_FILE)):
                    return path
            if CORE_FILE.split('/')[0] in dirs:
                if os.path.exists(os.path.join(root, CORE_FILE)):
                    return root
    return None

# 1. Mount Drive
if not os.path.exists('/content/drive'):
    try:
        drive.mount('/content/drive')
    except:
        print("⚠️ Drive mount skipped.")

# 2. Find Project
target_dir = locate_project()

# 3. Fallback: Git Clone or Upload
if not target_dir:
    print("\n❌ Project not found.")
    choice = input("Would you like to (1) Clone from GitHub or (2) Upload a ZIP? [Enter 1 or 2]: ")

    if choice == "1":
        repo_url = input("Enter your GitHub Repo URL: ")
        if repo_url:
            os.chdir("/content")
            !git clone {repo_url}
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
    print("\n❌ Setup failed. Please ensure the project folder is correctly uploaded.")
```
