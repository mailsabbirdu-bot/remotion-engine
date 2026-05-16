import os
import sys
import re
import time
import random
from core.browser_automator import BrowserAI

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
        scene_num_str = parts[i].strip()
        scene_text = parts[i+1].strip()

        # Convert Bangla numerals to English if necessary for indexing
        # but the user wants SC_01.wav, so we'll use a counter instead for filenames

        if scene_text:
            scenes.append(scene_text)

    print(f"✅ [PARSER] Found {len(scenes)} scenes.")
    return scenes

def main():
    print("🎙️ VOICEOVER ENGINE (V1.0) - ULTRA DEBUGGING MODE")
    print("==================================================")

    if not os.path.exists(STORY_FILE):
        print(f"❌ Error: {STORY_FILE} not found.")
        sys.exit(1)

    with open(STORY_FILE, "r", encoding="utf-8") as f:
        story_content = f.read()

    scenes = parse_scenes(story_content)

    if not scenes:
        print("⚠️ No scenes found in story.txt. Please check the file format.")
        sys.exit(0)

    # Initialize Browser
    browser_ai = BrowserAI(headless=True)
    print("🌐 [BROWSER] Initializing engine...")
    browser_ai.start()

    try:
        for i, scene_text in enumerate(scenes):
            scene_num = i + 1
            filename = f"SC_{scene_num:02d}.wav"
            output_path = os.path.join(AUDIO_DIR, filename)

            print(f"\n🎬 [PROCESS] Processing Scene {scene_num}/{len(scenes)}")
            print(f"📜 Text: {scene_text[:50]}...")

            # Step 1: Paste Text
            if not browser_ai.paste_text(scene_text):
                print(f"❌ Failed to paste text for Scene {scene_num}. Retrying...")
                time.sleep(2)
                if not browser_ai.paste_text(scene_text):
                    print(f"❌ Persistent failure for Scene {scene_num}. Skipping.")
                    continue

            # Step 2: Generate and Download
            if not browser_ai.generate_and_download(output_path):
                print(f"❌ Failed to generate/download Scene {scene_num}. Skipping.")
                continue

            print(f"✅ Scene {scene_num} completed: {filename}")

            # Random delay between scenes to avoid bot detection
            time.sleep(random.uniform(2, 5))

    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        browser_ai.close()
        print("\n🎉 TASK COMPLETED!")

if __name__ == "__main__":
    main()
