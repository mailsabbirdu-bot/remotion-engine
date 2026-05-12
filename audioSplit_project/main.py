import os
import re
import torch
import torchaudio
import shutil
from pydub import AudioSegment
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
    # Split by scene markers, keep content
    scenes = re.split(r'(?m)^(?:দৃশ্য|Scene)\s*(?:[০-৯\d]+)', content)
    return [s.strip() for s in scenes if s.strip()]

def clean_for_model(text, is_bangla):
    if is_bangla:
        # Keep Bangla unicode range, replace others with space
        text = re.sub(r'[^\u0980-\u09FF\s]', ' ', text)
    else:
        text = text.upper()
        text = re.sub(r'[^A-Z\s]', ' ', text)
    # Join with space to keep words distinct
    return "|".join(text.split()) # Use '|' as word separator for Wav2Vec2

def get_trellis(emissions, tokens, blank_id=0):
    num_frame = emissions.size(0)
    num_tokens = len(tokens)
    trellis = torch.empty((num_frame + 1, num_tokens + 1))
    trellis[0, 0] = 0
    trellis[1:, 0] = torch.cumsum(emissions[:, blank_id], 0)
    trellis[0, 1:] = -float("inf")
    trellis[-num_frame:, 1:] = float("-inf")

    for t in range(num_frame):
        trellis[t + 1, 1:] = torch.maximum(
            trellis[t, 1:] + emissions[t, blank_id],
            trellis[t, :-1] + emissions[t, tokens],
        )
    return trellis

def backtrack(trellis, emissions, tokens, blank_id=0):
    j = len(tokens)
    t = trellis.size(0) - 1
    path = []
    while j > 0:
        assert t > 0
        stay = trellis[t - 1, j] + emissions[t - 1, blank_id]
        change = trellis[t - 1, j - 1] + emissions[t - 1, tokens[j - 1]]
        if stay > change:
            pass
        else:
            path.append((t - 1, j - 1))
            j -= 1
        t -= 1
    return path[::-1]

def split_audio():
    print(f"🚀 GLOBAL TRELLIS ALIGNMENT ENGINE STARTING. DEVICE: {DEVICE}")

    if not os.path.exists(STORY_WAV):
        print(f"❌ Error: {STORY_WAV} not found!")
        return

    scenes_text = parse_story(STORY_TXT)
    if not scenes_text:
        print("❌ Error: No scenes found in story.txt")
        return

    is_bangla = bool(re.search(r'[\u0980-\u09FF]', " ".join(scenes_text)))
    model_id = "arijitx/wav2vec2-large-xlsr-bengali" if is_bangla else "facebook/wav2vec2-large-960h"

    print(f"🌍 Language: {'Bangla' if is_bangla else 'English'} | Model: {model_id}")

    processor = Wav2Vec2Processor.from_pretrained(model_id)
    model = Wav2Vec2ForCTC.from_pretrained(model_id).to(DEVICE)

    # Prepare master script for global alignment
    # We map tokens to scene indices
    master_tokens = []
    scene_token_ranges = []

    current_token_idx = 0
    for scene in scenes_text:
        cleaned = clean_for_model(scene, is_bangla)
        # Convert text to processor tokens
        # We handle word separators explicitly
        tokens = processor.tokenizer(cleaned, add_special_tokens=False).input_ids
        master_tokens.extend(tokens)
        scene_token_ranges.append((current_token_idx, current_token_idx + len(tokens)))
        current_token_idx += len(tokens)

    # Load audio
    waveform, sample_rate = torchaudio.load(STORY_WAV)
    if sample_rate != 16000:
        resampler = torchaudio.transforms.Resample(sample_rate, 16000)
        waveform = resampler(waveform)
    if waveform.shape[0] > 1: waveform = waveform[0:1]

    # Get emissions
    with torch.inference_mode():
        inputs = processor(waveform.squeeze(0), sampling_rate=16000, return_tensors="pt").to(DEVICE)
        emissions = torch.log_softmax(model(inputs.input_values).logits, dim=-1).squeeze(0).cpu()

    # Perform Trellis Alignment
    print("🧠 Calculating optimal global alignment path...")
    trellis = get_trellis(emissions, master_tokens)
    path = backtrack(trellis, emissions, master_tokens)

    # Calculate time per frame
    # Wav2Vec2 usually has 50 frames per second
    time_per_frame = waveform.shape[1] / emissions.shape[0] / 16000

    audio_full = AudioSegment.from_wav(STORY_WAV)
    total_len = len(audio_full)

    # Map token positions to timestamps
    token_timestamps = []
    for frame_idx, token_idx in path:
        token_timestamps.append(frame_idx * time_per_frame)

    print("✂️ Slicing audio files...")
    for i, (start_idx, end_idx) in enumerate(scene_token_ranges):
        # The start of the scene is the timestamp of its first token
        # The end of the scene is the timestamp of its last token (end_idx - 1)
        if start_idx >= len(token_timestamps): continue

        start_s = token_timestamps[start_idx]
        # Use next scene's start or end of audio as end point for perfect continuity
        if i + 1 < len(scene_token_ranges):
            next_start_idx = scene_token_ranges[i+1][0]
            end_s = token_timestamps[next_start_idx] if next_start_idx < len(token_timestamps) else token_timestamps[-1]
        else:
            end_s = total_len / 1000

        output_name = f"SC_{str(i+1).zfill(2)}.wav"
        output_path = os.path.join(AUDIO_DIR, output_name)

        start_ms, end_ms = start_s * 1000, end_s * 1000
        segment = audio_full[start_ms:end_ms]
        segment.export(output_path, format="wav")

        print(f"   ✅ Saved: {output_name} [{round(start_s, 2)}s - {round(end_s, 2)}s]")

    print("\n🎉 Precision alignment complete! Drift eliminated.")

if __name__ == "__main__":
    split_audio()
