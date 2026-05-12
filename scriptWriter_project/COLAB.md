# 🎬 Universal ScriptWriter AI - One-Cell Setup

Paste and run this entire cell in Google Colab. It handles mounting, cloning, and running the AI automatically.

```python
import os
import subprocess
import sys

# --- CONFIGURATION ---
REPO_URL = "https://github.com/your-username/your-repo-name.git" # <-- CHANGE THIS to your actual repo URL
PROJECT_NAME = "scriptWriter_project"
# ---------------------

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

print("🚀 Starting Universal Setup...")

# 1. Mount Google Drive
try:
    from google.colab import drive
    if not os.path.exists('/content/drive'):
        drive.mount('/content/drive')
    print("✅ Google Drive mounted.")
except Exception as e:
    print(f"⚠️ Drive mount skipped: {e}")

# 2. Locate Project
print(f"🔍 Locating {PROJECT_NAME}...")

target_path = None
# Check 1: Local /content
if os.path.exists(f"/content/{PROJECT_NAME}"):
    target_path = f"/content/{PROJECT_NAME}"
# Check 2: Inside a cloned repo in /content
elif not target_path:
    for item in os.listdir("/content"):
        potential = os.path.join("/content", item, PROJECT_NAME)
        if os.path.isdir(potential):
            target_path = potential
            break
# Check 3: Google Drive
if not target_path and os.path.exists("/content/drive/MyDrive"):
    print("📂 Searching Google Drive (this may take a few seconds)...")
    for root, dirs, files in os.walk("/content/drive/MyDrive"):
        if PROJECT_NAME in dirs:
            target_path = os.path.join(root, PROJECT_NAME)
            break

# 3. Auto-Clone if missing
if not target_path:
    print(f"❌ Project not found. Cloning from GitHub: {REPO_URL}...")
    os.chdir("/content")
    res = run_cmd(f"git clone {REPO_URL}")
    if res.returncode == 0:
        # Re-search after clone
        for item in os.listdir("/content"):
            potential = os.path.join("/content", item, PROJECT_NAME)
            if os.path.isdir(potential):
                target_path = potential
                break
    else:
        print(f"⚠️ Clone failed: {res.stderr}")
        print("Please manually upload the 'scriptWriter_project' folder to your Google Drive or Colab.")
        sys.exit("Setup stopped.")

if target_path:
    print(f"✅ Project active at: {target_path}")
    os.chdir(target_path)
else:
    sys.exit("❌ Fatal error: Project directory still not found.")

# 4. Install Dependencies
print("\n📦 Installing AI components...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--quiet"])
print("✅ Components ready.")

# 5. Execute
print("\n" + "="*40)
print("🎬 SCRIPTWRITER AI IS READY")
print("="*40 + "\n")

!python main.py
```

## Troubleshooting:
- **"Project not found"**: If the auto-clone fails, make sure you have the `scriptWriter_project` folder uploaded to your Google Drive in a location Colab can see.
- **Drive connection**: If you don't see your files, ensure you clicked "Allow" on the Google Drive pop-up.
- **Output**: The final script will always be saved to `Counterism_Studio_V4/audio/script.txt` on your Drive.
