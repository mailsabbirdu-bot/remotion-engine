import os
import sys
import re
import time
import random
from core.voice_ai import VoiceAI

# Path discovery for Colab vs Local
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

AUDIO_DIR = os.path.join(BASE, "audio")
STORY_FILE = os.path.join(AUDIO_DIR, "story.txt")

def parse_scenes(story_content):
    """
    Parses story.txt and extracts text for each scene.
    Supports both English (Scene X) and Bangla (দৃশ্য X).
    """
    print("🔍 [PARSER] Parsing scenes from story content...")

    # Split by scene markers
    pattern = r"(?m)^(?:Scene|দৃশ্য)\s*([\d০-৯]+)\s*$"

    parts = re.split(pattern, story_content)

    scenes = []
    # Parts will be [text_before, scene_num, scene_text, scene_num, scene_text, ...]
    for i in range(1, len(parts), 2):
        scene_text = parts[i+1].strip()
        if scene_text:
            scenes.append(scene_text)

    print(f"✅ [PARSER] Found {len(scenes)} scenes.")
    return scenes

def main():
    print("🎙️ VOICEOVER ENGINE (V2.0) - API EDITION")
    print("==================================================")

    if not os.path.exists(STORY_FILE):
        print(f"❌ Error: {STORY_FILE} not found.")
        # Create dummy directory for testing if not exists on local
        if BASE == LOCAL_BASE:
            os.makedirs(AUDIO_DIR, exist_ok=True)
            print(f"🛠️ Created local directory: {AUDIO_DIR}")
        else:
            sys.exit(1)

    if not os.path.exists(STORY_FILE):
        print("⚠️ No story.txt found. Please provide a story.txt in the audio folder.")
        sys.exit(0)

    with open(STORY_FILE, "r", encoding="utf-8") as f:
        story_content = f.read()

    scenes = parse_scenes(story_content)

    if not scenes:
        print("⚠️ No scenes found in story.txt. Please check the file format.")
        sys.exit(0)

    # Initialize Voice AI
    try:
        voice_ai = VoiceAI()
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        sys.exit(1)

    print(f"🚀 Starting generation for {len(scenes)} scenes...")

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
            print(f"📜 Text: {scene_text[:100]}...")

            # Generate and Save
            success = voice_ai.generate_speech(scene_text, output_path)

            if not success:
                print(f"❌ Failed to generate Scene {scene_num}. Retrying once...")
                time.sleep(2)
                success = voice_ai.generate_speech(scene_text, output_path)
                if not success:
                    print(f"❌ Persistent failure for Scene {scene_num}. Skipping.")
                    continue

            print(f"✅ Scene {scene_num} completed: {filename}")

            # Brief delay to be polite to the API
            time.sleep(1)

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🎉 TASK COMPLETED!")

if __name__ == "__main__":
    main()
