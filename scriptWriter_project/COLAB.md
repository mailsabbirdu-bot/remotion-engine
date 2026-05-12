# Google Colab Setup for ScriptWriter AI

Run this cell in Google Colab to set up and run the ScriptWriter AI. This script will automatically find the project folder whether it's in your local Colab environment or on your Google Drive.

```python
import os
import subprocess
import sys

# 1. Mount Google Drive
try:
    from google.colab import drive
    if not os.path.exists('/content/drive'):
        drive.mount('/content/drive')
    print("✅ Google Drive mounted.")
except Exception as e:
    print(f"⚠️ Drive mount skipped or failed: {e}")

# 2. Advanced Project Discovery
PROJECT_NAME = "scriptWriter_project"

def find_project_dir(start_path):
    print(f"🔍 Searching for '{PROJECT_NAME}' in {start_path}...")
    for root, dirs, files in os.walk(start_path):
        if PROJECT_NAME in dirs:
            return os.path.join(root, PROJECT_NAME)
    return None

# Check common locations first for speed
fast_search_paths = [
    f"/content/{PROJECT_NAME}",
    f"/content/drive/MyDrive/{PROJECT_NAME}",
    f"/content/drive/MyDrive/Counterism_Studio_V4/{PROJECT_NAME}"
]

target_dir = None
for path in fast_search_paths:
    if os.path.exists(path):
        target_dir = path
        break

# If not found, do a deep search in /content
if not target_dir:
    target_dir = find_project_dir("/content")

if target_dir:
    print(f"✅ Found project at: {target_dir}")
    os.chdir(target_dir)
else:
    print(f"❌ Could not find '{PROJECT_NAME}' directory automatically.")
    print("Please ensure you have cloned the repository or uploaded the folder.")
    manual_path = input("Enter the path manually (or leave blank to exit): ")
    if manual_path and os.path.exists(manual_path):
        os.chdir(manual_path)
    else:
        sys.exit("Exiting setup.")

# 3. Install Dependencies
print("\n📦 Installing dependencies (this may take a minute)...")
try:
    # Check if requirements.txt exists in current dir
    if os.path.exists("requirements.txt"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed.")
    else:
        print("⚠️ 'requirements.txt' not found in the project directory!")
except Exception as e:
    print(f"❌ Error installing dependencies: {e}")

# 4. Run the Program
print("\n🚀 Starting ScriptWriter AI...\n")
if os.path.exists("main.py"):
    !python main.py
else:
    print("❌ 'main.py' not found in the current directory!")
```

## How to use:
1. Open Google Colab.
2. Paste the code above into a cell and run it.
3. If you just cloned a repository, the script will search through it to find the `scriptWriter_project` folder.
4. Enter your topic when prompted and hit Enter.
5. The final script will be saved to your Google Drive at `Counterism_Studio_V4/audio/script.txt`.
