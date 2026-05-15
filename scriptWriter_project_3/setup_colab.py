import os
import sys

def verify_environment():
    print("🧪 Verifying Browser-Based ScriptWriter Environment...")

    # 1. Check folder structure
    required_files = ["main.py", "requirements.txt", "core/config.py", "core/pipeline.py"]
    missing = []
    for f in required_files:
        if not os.path.exists(f):
            missing.append(f)

    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    else:
        print("✅ Core files present.")

    # 2. Check Drive Output Path
    DRIVE_PATH = "/content/drive/MyDrive/Counterism_Studio_V4/audio"
    if os.path.exists("/content/drive"):
        os.makedirs(DRIVE_PATH, exist_ok=True)
        print(f"✅ Output directory ready: {DRIVE_PATH}")
    else:
        print("ℹ️ Google Drive not mounted yet. Local mode will be used.")

    print("\n🚀 Environment check PASSED. Ready to run main.py")
    return True

if __name__ == "__main__":
    verify_environment()
