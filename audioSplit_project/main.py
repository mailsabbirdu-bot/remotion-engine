import os
import re
import whisper
import shutil
from pydub import AudioSegment
from fuzzywuzzy import fuzz

# =========================================================
# PATH CONFIGURATION
# =========================================================
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE
AUDIO_DIR = os.path.join(BASE, "audio")

STORY_WAV = os.path.join(AUDIO_DIR, "story.wav")
STORY_TXT = os.path.join(AUDIO_DIR, "story.txt")

os.makedirs(AUDIO_DIR, exist_ok=True)

def parse_story(txt_path):
    """Parses story.txt into individual scenes."""
    if not os.path.exists(txt_path):
        print(f"❌ Error: {txt_path} not found!")
        return []

    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by "দৃশ্য [সংখ্যা]" or "Scene [number]" (Supports both Bangla and English)
    # The regex looks for markers at the start of a line.
    scenes = re.split(r'(?m)^(?:দৃশ্য|Scene)\s*(?:[০-৯\d]+)', content)

    # Filter out empty strings and strip whitespace
    scenes = [s.strip() for s in scenes if s.strip()]
    return scenes

def clean_text(text):
    """Normalizes text for better matching."""
    # Remove punctuation while preserving characters from all languages.
    # We explicitly remove common punctuation marks instead of using \w which can be restrictive for some scripts.
    cleaned = re.sub(r'[।!,.;:?\"\'\(\)\[\]\{\}]', '', text)
    return cleaned.lower().strip()

def split_audio():
    print(f"🚀 AUDIO SPLIT ENGINE STARTING. BASE: {BASE}")

    if not os.path.exists(STORY_WAV):
        print(f"❌ Error: {STORY_WAV} not found!")
        return

    scenes_text = parse_story(STORY_TXT)
    if not scenes_text:
        print("❌ Error: No scenes found in story.txt or file is empty.")
        return

    print(f"📖 Found {len(scenes_text)} scenes. Loading Whisper model...")
    # 'base' model is a good middle ground for speed and accuracy.
    # Use 'small' or 'medium' if higher accuracy is needed for complex audio.
    model = whisper.load_model("base")

    print("🎙️ Transcribing story.wav (this might take a few minutes)...")
    # For better alignment, we just need the segments.
    result = model.transcribe(STORY_WAV)
    segments = result['segments']

    print("✂️ Loading audio file for slicing...")
    full_audio = AudioSegment.from_wav(STORY_WAV)

    current_seg_idx = 0
    num_segments = len(segments)

    for i, scene_raw_text in enumerate(scenes_text):
        scene_clean = clean_text(scene_raw_text)
        print(f"\n🎬 Processing Scene {i+1}/{len(scenes_text)}...")

        best_end_idx = current_seg_idx
        max_ratio = 0
        accumulated_text = ""

        # We search forward from the current segment index to find the best match for this scene
        temp_idx = current_seg_idx
        while temp_idx < num_segments:
            seg_text = clean_text(segments[temp_idx]['text'])
            accumulated_text += " " + seg_text

            # Using partial_ratio because the accumulated text might be longer than the scene text
            ratio = fuzz.partial_ratio(scene_clean, accumulated_text)

            if ratio > 70: # Threshold for a decent match
                if ratio >= max_ratio:
                    max_ratio = ratio
                    best_end_idx = temp_idx
                else:
                    # If ratio starts to drop significantly, we've likely passed the scene
                    if max_ratio - ratio > 15:
                        break

            temp_idx += 1
            # Safety break if we've accumulated way more text than expected
            if len(accumulated_text) > len(scene_clean) * 2 + 100:
                break

        if max_ratio > 40: # Flexible threshold for alignment
            start_time = segments[current_seg_idx]['start'] * 1000 # convert to ms
            end_time = segments[best_end_idx]['end'] * 1000
            current_seg_idx = best_end_idx + 1

            print(f"   ✨ Match found (Score: {max_ratio})")
        else:
            print(f"   ⚠️ Warning: Weak match for Scene {i+1}. Using segment heuristic.")
            # Fallback: take at least one segment if available
            if current_seg_idx < num_segments:
                start_time = segments[current_seg_idx]['start'] * 1000
                end_time = segments[current_seg_idx]['end'] * 1000
                current_seg_idx += 1
            else:
                print(f"   ❌ Could not find audio for Scene {i+1}")
                continue

        # Slice and export
        output_name = f"SC_{str(i+1).zfill(2)}.wav"
        output_path = os.path.join(AUDIO_DIR, output_name)

        # Add 100ms padding if possible for smoother transitions
        scene_audio = full_audio[max(0, start_time - 100):min(len(full_audio), end_time + 100)]
        scene_audio.export(output_path, format="wav")
        print(f"   ✅ Saved: {output_name} [{round(start_time/1000, 1)}s - {round(end_time/1000, 1)}s]")

    print("\n🎉 Audio splitting complete! Files are in your Google Drive audio folder.")

if __name__ == "__main__":
    split_audio()
