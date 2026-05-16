import os
import sys
import re
import time
import subprocess
from core.xtts_engine import XTTSEngine

# --- ULTRA DEBUGGING: SYSTEM INFO ---
def print_ultra_debug():
    print("\n" + "="*50)
    print("🔬 ULTRA DEBUGGING MODE - SYSTEM REPORT")
    print("="*50)
    print(f"🐍 Python Version: {sys.version}")
    print(f"🚀 Python Executable: {sys.executable}")
    print(f"📂 Current Working Directory: {os.getcwd()}")

    try:
        import torch
        print(f"🔥 Torch Version: {torch.__version__}")
        print(f"🎮 CUDA Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"📼 GPU Name: {torch.cuda.get_device_name(0)}")
    except ImportError:
        print("❌ Torch not installed.")

    print("\n📦 Environment Variables:")
    print(f"   COQUI_TOS_AGREED: {os.environ.get('COQUI_TOS_AGREED')}")

    print("\n📂 Project Structure:")
    for root, dirs, files in os.walk("."):
        level = root.replace(".", "").count(os.sep)
        indent = " " * 4 * (level)
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 4 * (level + 1)
        for f in files:
            print(f"{subindent}{f}")
    print("="*50 + "\n")

# --- PATH DISCOVERY ---
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

AUDIO_DIR = os.path.join(BASE, "audio")
STORY_FILE = os.path.join(AUDIO_DIR, "story.txt")
CLONE_WAV = os.path.join(AUDIO_DIR, "clone.wav")

def parse_scenes(story_content):
    """
    Parses story.txt and extracts text for each scene.
    Supports both English (Scene X) and Bangla (দৃশ্য X).
    """
    print("🔍 [PARSER] Parsing scenes from story content...")
    # Split by scene markers: Scene 1 or দৃশ্য ১
    pattern = r"(?m)^(?:Scene|দৃশ্য)\s*([\d০-৯]+)\s*$"

    parts = re.split(pattern, story_content)

    scenes = []
    # Parts will be [text_before, scene_num, scene_text, scene_num, scene_text, ...]
    for i in range(1, len(parts), 2):
        scene_text = parts[i+1].strip()
        if scene_text:
            # Clean up the text: remove double newlines and extra spaces
            scene_text = re.sub(r'\n+', '\n', scene_text).strip()
            scenes.append(scene_text)

    print(f"✅ [PARSER] Found {len(scenes)} scenes.")
    return scenes

def main():
    print_ultra_debug()

    print("🎙️ VOICEOVER ENGINE (V2.0) - COQUI XTTS EDITION")
    print("==================================================")

    if not os.path.exists(AUDIO_DIR):
        print(f"🛠️ [INIT] Creating audio directory: {AUDIO_DIR}")
        os.makedirs(AUDIO_DIR, exist_ok=True)

    if not os.path.exists(STORY_FILE):
        print(f"❌ Error: {STORY_FILE} not found. Please ensure story.txt exists in the audio folder.")
        sys.exit(1)

    if not os.path.exists(CLONE_WAV):
        print(f"⚠️ Warning: {CLONE_WAV} not found. Voice cloning might fail or use default.")
        # We'll let the engine handle the missing file error for better debug info

    with open(STORY_FILE, "r", encoding="utf-8") as f:
        story_content = f.read()

    scenes = parse_scenes(story_content)

    if not scenes:
        print("⚠️ No scenes found in story.txt. Please check the file format.")
        sys.exit(0)

    # Initialize XTTS Engine
    try:
        engine = XTTSEngine()
    except Exception as e:
        print(f"❌ Engine initialization failed: {e}")
        sys.exit(1)

    print(f"🚀 Starting generation for {len(scenes)} scenes...")

    start_time = time.time()

    try:
        for i, scene_text in enumerate(scenes):
            scene_num = i + 1
            filename = f"SC_{scene_num:02d}.wav"
            output_path = os.path.join(AUDIO_DIR, filename)

            # Skip if already exists
            if os.path.exists(output_path):
                print(f"⏩ [SKIP] Scene {scene_num} already exists: {filename}")
                continue

            print(f"\n🎬 [PROCESS] Processing Scene {scene_num}/{len(scenes)}")
            print(f"📜 Text Snippet: {scene_text[:150]}...")

            scene_start = time.time()
            success = engine.generate_speech(scene_text, output_path, CLONE_WAV)
            scene_end = time.time()

            if success:
                print(f"✅ Scene {scene_num} completed in {scene_end - scene_start:.2f}s: {filename}")
            else:
                print(f"❌ Failed to generate Scene {scene_num}.")

    except KeyboardInterrupt:
        print("\n🛑 Process interrupted by user.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        total_time = time.time() - start_time
        print("\n" + "="*50)
        print(f"🎉 TASK COMPLETED in {total_time:.2f}s")
        print("="*50)

if __name__ == "__main__":
    main()
