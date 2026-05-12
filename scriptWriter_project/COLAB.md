# Google Colab Setup for ScriptWriter AI

Run this cell in Google Colab to set up and run the ScriptWriter AI. This script will automatically find the project folder whether it's in your local Colab environment or on your Google Drive.

```python
import os
import subprocess
import sys

# 1. Mount Google Drive (Recommended)
try:
    from google.colab import drive
    if not os.path.exists('/content/drive'):
        drive.mount('/content/drive')
    print("✅ Google Drive mounted.")
except Exception as e:
    print(f"⚠️ Drive mount skipped or failed: {e}")

# 2. Find Project Directory
PROJECT_NAME = "scriptWriter_project"
search_paths = [
    f"/content/{PROJECT_NAME}",
    f"/content/drive/MyDrive/{PROJECT_NAME}",
    f"/content/drive/MyDrive/Counterism_Studio_V4/{PROJECT_NAME}",
    f"./{PROJECT_NAME}"
]

target_dir = None
for path in search_paths:
    if os.path.exists(path):
        target_dir = path
        break

if target_dir:
    print(f"✅ Found project at: {target_dir}")
    os.chdir(target_dir)
else:
    print(f"❌ Could not find '{PROJECT_NAME}' directory automatically.")
    print("Please make sure you have uploaded the project to Colab or your Drive.")
    # Fallback: Ask user for path
    manual_path = input("Enter the path to scriptWriter_project manually (or leave blank to exit): ")
    if manual_path and os.path.exists(manual_path):
        os.chdir(manual_path)
    else:
        sys.exit("Exiting setup.")

# 3. Install Dependencies
print("\n📦 Installing dependencies (this may take a minute)...")
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Dependencies installed.")
except Exception as e:
    print(f"❌ Error installing dependencies: {e}")

# 4. Run the Program
print("\n🚀 Starting ScriptWriter AI...\n")
!python main.py
```

## How to use:
1. Open Google Colab.
2. Paste the code above into a cell and run it.
3. If the project is on your Google Drive, make sure it is named `scriptWriter_project`.
4. Enter your topic when prompted and hit Enter.
5. The final script will be saved to your Google Drive at `Counterism_Studio_V4/audio/script.txt`.
