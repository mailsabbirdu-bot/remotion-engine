import os
import re
import shutil
import torch
import torchaudio
from pydub import AudioSegment
from fuzzywuzzy import fuzz
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

# =========================================================
# PATH CONFIGURATION
# =========================================================
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE
AUDIO_DIR = os.path.join(BASE, "audio")

STORY_WAV = os.path.join(AUDIO_DIR, "story.wav")
STORY_TXT = os.path.join(AUDIO_DIR, "story.txt")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def parse_story(txt_path):
    if not os.path.exists(txt_path):
        return []
    with open(txt_path, "r", encoding="utf-8") as f:
        content = f.read()
    scenes = re.split(r'(?m)^(?:দৃশ্য|Scene)\s*(?:[০-৯\d]+)', content)
    return [s.strip() for s in scenes if s.strip()]

def clean_for_model(text, is_bangla):
    if is_bangla:
        # For Bangla XLS-R models, we usually keep Bangla characters but remove punctuation
        # This regex keeps Bangla unicode range
        text = re.sub(r'[^\u0980-\u09FF\s]', '', text)
    else:
        # For English, uppercase and remove non-alpha
        text = text.upper()
        text = re.sub(r'[^A-Z\s]', '', text)
    return " ".join(text.split())

def split_audio():
    print(f"🚀 FORCED ALIGNMENT ENGINE STARTING. DEVICE: {DEVICE}")

    if not os.path.exists(STORY_WAV):
        print(f"❌ Error: {STORY_WAV} not found!")
        return

    scenes_text = parse_story(STORY_TXT)
    if not scenes_text:
        print("❌ Error: No scenes found in story.txt")
        return

    full_script = " ".join(scenes_text)
    is_bangla = bool(re.search(r'[\u0980-\u09FF]', full_script))

    # Select Model
    model_id = "arijitx/wav2vec2-large-xlsr-bengali" if is_bangla else "facebook/wav2vec2-large-960h"
    print(f"🌍 Language: {'Bangla' if is_bangla else 'English'} | Model: {model_id}")

    processor = Wav2Vec2Processor.from_pretrained(model_id)
    model = Wav2Vec2ForCTC.from_pretrained(model_id).to(DEVICE)

    # Load and Preprocess Audio
    waveform, sample_rate = torchaudio.load(STORY_WAV)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
        waveform = resampler(waveform)

    # Take first channel if stereo
    if waveform.shape[0] > 1:
        waveform = waveform[0:1]

    # Inference to get emissions and word-level timestamps
    with torch.inference_mode():
        inputs = processor(waveform.squeeze(0), sampling_rate=16000, return_tensors="pt").to(DEVICE)
        outputs = model(inputs.input_values)
        logits = outputs.logits

    # Using the processor's output to get word timestamps
    # Note: Wav2Vec2 output doesn't directly give timestamps without some processing
    # We use a robust approach: find the indices of the scene-end words in the decoded transcript
    predicted_ids = torch.argmax(logits, dim=-1)[0]
    # retrieve word-level information
    decoded = processor.decode(predicted_ids, output_word_offsets=True)

    word_offsets = decoded.word_offsets
    # Calculate seconds per offset (stride)
    # The stride for Wav2Vec2 is usually 20ms (50 frames per second)
    time_per_offset = model.config.inputs_to_logits_ratio / 16000

    transcript_words = [clean_for_model(w['word'], is_bangla) for w in word_offsets]
    word_timestamps = [(w['start_offset'] * time_per_offset, w['end_offset'] * time_per_offset) for w in word_offsets]

    print(f"📝 Transcribed {len(transcript_words)} words from audio.")

    audio_full = AudioSegment.from_wav(STORY_WAV)
    total_duration_ms = len(audio_full)

    current_word_idx = 0
    num_transcript_words = len(transcript_words)

    for i, scene_text in enumerate(scenes_text):
        scene_clean = clean_for_model(scene_text, is_bangla)
        scene_words = scene_clean.split()
        if not scene_words: continue

        print(f"🎬 Slicing Scene {i+1}...")

        # Find the best match for the scene in the transcript starting from current position
        best_end_idx = current_word_idx
        max_fuzz = -1

        accumulated = ""
        # Search window: proportional to scene length with a buffer
        search_limit = min(current_word_idx + len(scene_words) * 2 + 10, num_transcript_words)

        for j in range(current_word_idx, search_limit):
            accumulated += " " + transcript_words[j]
            score = fuzz.ratio(scene_clean, accumulated.strip())
            if score >= max_fuzz:
                max_fuzz = score
                best_end_idx = j
            if score > 95: break
            if max_fuzz > 60 and (max_fuzz - score) > 20: break

        start_time_s = word_timestamps[current_word_idx][0] if current_word_idx < num_transcript_words else 0
        end_time_s = word_timestamps[best_end_idx][1] if best_end_idx < num_transcript_words else total_duration_ms/1000

        # Update pointer
        current_word_idx = best_end_idx + 1

        # ms conversion
        start_ms = start_time_s * 1000
        end_ms = end_time_s * 1000

        # Export
        output_name = f"SC_{str(i+1).zfill(2)}.wav"
        output_path = os.path.join(AUDIO_DIR, output_name)

        # Add padding
        segment = audio_full[max(0, start_ms - 200):min(total_duration_ms, end_ms + 200)]
        segment.export(output_path, format="wav")

        print(f"   ✅ Saved: {output_name} ({round(start_ms/1000, 1)}s - {round(end_ms/1000, 1)}s)")

    print("\n🎉 Forced alignment splitting complete!")

if __name__ == "__main__":
    split_audio()
