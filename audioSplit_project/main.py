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
    # 'small' is better for multilingual than 'base'.
    model = whisper.load_model("small")

    print("🎙️ Transcribing story.wav with AI Timestamps (this may take a moment)...")
    # Using word_timestamps for high-precision cutting
    result = model.transcribe(STORY_WAV, word_timestamps=True)

    # Flatten all words into a single list with timestamps
    all_words = []
    for segment in result['segments']:
        for word in segment.get('words', []):
            all_words.append({
                'text': clean_text(word['word']),
                'start': word['start'],
                'end': word['end']
            })

    if not all_words:
        print("❌ Error: No speech detected in story.wav")
        return

    print("✂️ Loading audio file for slicing...")
    full_audio = AudioSegment.from_wav(STORY_WAV)

    current_word_idx = 0
    num_words = len(all_words)

    for i, scene_raw_text in enumerate(scenes_text):
        scene_clean = clean_text(scene_raw_text)
        scene_words = scene_clean.split()
        print(f"\n🎬 Processing Scene {i+1}/{len(scenes_text)}...")

        if not scene_words:
            continue

        # Look for the last word of the scene in the transcript to find the split point
        best_end_idx = current_word_idx
        max_score = -1

        # Search window: from current position up to a reasonable limit
        # We try to find where the scene ends by matching the accumulated transcript text
        accumulated_transcript = ""
        search_limit = min(current_word_idx + len(scene_words) * 3 + 20, num_words)

        for j in range(current_word_idx, search_limit):
            accumulated_transcript += " " + all_words[j]['text']
            score = fuzz.ratio(scene_clean, accumulated_transcript.strip())

            if score > max_score:
                max_score = score
                best_end_idx = j

            # If we have an excellent match, we can stop early
            if score > 95:
                break

            # If the score starts dropping significantly, we've passed it
            if max_score > 60 and (max_score - score) > 20:
                break

        start_time = all_words[current_word_idx]['start'] * 1000
        end_time = all_words[best_end_idx]['end'] * 1000

        print(f"   ✨ Alignment: {round(max_score)}% match.")
        current_word_idx = best_end_idx + 1

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
