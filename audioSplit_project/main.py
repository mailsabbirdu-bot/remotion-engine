import os
import re
import whisper
import stable_whisper
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

    # Join all scene text to use as a prompt for Whisper
    full_script_text = " ".join(scenes_text)

    # Detect language: Check for Bangla characters
    is_bangla = bool(re.search(r'[\u0980-\u09FF]', full_script_text))
    lang_code = "bn" if is_bangla else "en"
    print(f"🌍 Detected Language: {'Bangla' if is_bangla else 'English'} ({lang_code})")

    print(f"📖 Found {len(scenes_text)} scenes. Loading Stable-Whisper model...")
    # stable_whisper provides much more accurate word-level timestamps
    model = stable_whisper.load_model("small")

    print("🎙️ Transcribing story.wav with AI Alignment...")
    # Passing the script as 'initial_prompt' significantly helps Whisper with specialized vocabulary
    result = model.transcribe(
        STORY_WAV,
        language=lang_code,
        initial_prompt=full_script_text[:1000]
    )

    # Flatten all words into a single list with timestamps
    all_words = []
    for word in result.all_words():
        word_text = clean_text(word.word)
        if word_text:
            all_words.append({
                'text': word_text,
                'start': word.start,
                'end': word.end
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
        print(f"\n🎬 Processing Scene {i+1}/{len(scenes_text)}...")

        if not scene_clean or current_word_idx >= num_words:
            print(f"   ⚠️ Skipping Scene {i+1} (No script or end of audio reached)")
            continue

        # Matching algorithm: Sliding window to find the best end point for this scene
        best_end_idx = current_word_idx
        max_score = -1

        # We search forward in the transcript to find where the current scene script ends
        accumulated_transcript = ""
        # Look ahead up to 2.5x the number of words in the scene script + buffer
        look_ahead = len(scene_clean.split()) * 2 + 30
        search_limit = min(current_word_idx + look_ahead, num_words)

        for j in range(current_word_idx, search_limit):
            accumulated_transcript += " " + all_words[j]['text']

            # token_sort_ratio is more robust against word order or extra small words
            score = fuzz.token_sort_ratio(scene_clean, accumulated_transcript.strip())

            if score >= max_score:
                max_score = score
                best_end_idx = j

            # Early exit for perfect matches
            if score > 98: break
            # Drop-off check: if score is falling from a high peak, we likely passed it
            if max_score > 70 and (max_score - score) > 25: break

        start_time = all_words[current_word_idx]['start'] * 1000
        end_time = all_words[best_end_idx]['end'] * 1000

        # Print first few words matched for user verification
        matched_text = " ".join([w['text'] for w in all_words[current_word_idx:best_end_idx+1]])
        print(f"   🔍 AI Matched: \"{matched_text[:60]}...\"")
        print(f"   ✨ Confidence: {round(max_score)}%")

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
