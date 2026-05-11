# =========================================================
# COUNTERISM AUDIO-FIRST RENDER ENGINE (FINAL FIXED)
# =========================================================

import nest_asyncio
nest_asyncio.apply()

import os
import json
import asyncio
import aiohttp
import random
import subprocess
import shutil

from pydub import AudioSegment
from core.scout import get_all_candidates

# Path discovery for Colab vs Local
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

PLAN_PATH = f"{BASE}/manifests/production_plan.json"
TEMP_DIR = "/content/temp_assets" if os.path.exists("/content") else "./temp_assets"
RENDER_DIR = f"{BASE}/renders"
FINAL_OUTPUT = f"{BASE}/final_video.mp4"
AUDIO_DIR = f"{BASE}/audio"

os.makedirs(RENDER_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(os.path.dirname(PLAN_PATH), exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

print(f"🚀 ENGINE STARTING. BASE: {BASE}")

def cleanup():
    print("🧹 CLEARING OLD OUTPUTS...")
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    # We only clear renders if they exist
    if os.path.exists(RENDER_DIR):
        for f in os.listdir(RENDER_DIR):
            os.remove(os.path.join(RENDER_DIR, f))

    if os.path.exists(FINAL_OUTPUT):
        os.remove(FINAL_OUTPUT)

cleanup()

START_PADDING = 0.5
END_PADDING = 0.5

# =========================================================
# AUDIO SYNC
# =========================================================

def update_scene_durations_from_audio():
    if not os.path.exists(PLAN_PATH):
        print(f"⚠️ Warning: {PLAN_PATH} not found. Creating a dummy plan.")
        data = {"scenes": [{"scene_id": "scene_1", "text": "test"}]}
    else:
        with open(PLAN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

    scenes = data["scenes"]

    print("\n🎙️ SCANNING AUDIO FILES...\n")

    for idx, scene in enumerate(scenes, start=1):
        audio_name = f"SC_{idx:02d}.wav"
        audio_path = os.path.join(AUDIO_DIR, audio_name)

        if not os.path.exists(audio_path):
            print(f"⚠️ Missing audio: {audio_name}. Using default 5s.")
            scene["duration"] = 5.0
            scene["audio_path"] = ""
            scene["audio_start_in_scene"] = 0.0
            continue

        audio = AudioSegment.from_wav(audio_path)
        raw = len(audio) / 1000.0

        final = START_PADDING + raw + END_PADDING

        scene["audio_path"] = audio_path
        scene["audio_start_in_scene"] = START_PADDING
        scene["duration"] = round(final, 2)

        print(f"✅ {audio_name} → {round(final,2)}s")

    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return scenes

# =========================================================
# DOWNLOAD
# =========================================================

async def download_asset(url, path):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as r:
                if r.status != 200:
                    return False
                with open(path, "wb") as f:
                    f.write(await r.read())
        return True
    except:
        return False

# =========================================================
# RENDER VIDEO (FIXED)
# =========================================================

def render_video(video, audio, out, duration, delay):
    # Using /tmp for fastest IO in Colab
    temp_v = "/tmp/temp_v.mp4"

    # Step 1: Scale and Loop Video
    # We use -preset superfast for Colab speed
    subprocess.run([
        "ffmpeg","-y",
        "-stream_loop","-1",
        "-i",video,
        "-t",str(duration),
        "-vf","scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1",
        "-r","24",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-preset", "superfast",
        "-an",
        temp_v
    ], check=True, capture_output=True)

    # Step 2: Mux Audio with Offset
    if audio and os.path.exists(audio):
        subprocess.run([
            "ffmpeg","-y",
            "-i",temp_v,
            "-itsoffset",str(delay),
            "-i",audio,
            "-map","0:v",
            "-map","1:a",
            "-c:v","copy",
            "-c:a","aac",
            "-b:a", "128k",
            "-shortest",
            out
        ], check=True, capture_output=True)
    else:
        # If no audio, just move the video
        shutil.move(temp_v, out)

# =========================================================
# PROCESS SCENE
# =========================================================

async def process_scene(scene, idx):
    print(f"\n🎬 PROCESSING {scene['scene_id']}")

    candidates = await get_all_candidates(scene)
    if not candidates:
        print("❌ NO ASSETS FOUND")
        return None

    # Pick best candidate or random from top 3 for variety
    best = candidates[0]

    ext = ".mp4" if best["type"]=="video" else ".jpg"
    asset_path = f"{TEMP_DIR}/asset_{idx}{ext}"

    print(f"📥 Downloading: {best['source']} ({best['type']})")
    ok = await download_asset(best["url"], asset_path)
    if not ok:
        print("❌ DOWNLOAD FAILED")
        return None

    out = f"{RENDER_DIR}/scene_{idx}.mp4"

    print(f"⚙️ Rendering Scene {idx}...")
    try:
        render_video(
            asset_path,
            scene.get("audio_path"),
            out,
            scene["duration"],
            scene.get("audio_start_in_scene", 0)
        )
        return out
    except Exception as e:
        print(f"❌ RENDER FAILED: {e}")
        return None

# =========================================================
# FINAL MERGE
# =========================================================

def merge_all(scene_files):
    if not scene_files:
        print("❌ No scenes to merge!")
        return

    list_path = "/tmp/concat_list.txt"
    with open(list_path,"w") as f:
        for s in scene_files:
            # Ensure absolute path for ffmpeg concat
            abs_s = os.path.abspath(s)
            f.write(f"file '{abs_s}'\n")

    print("🧩 Merging all scenes...")
    subprocess.run([
        "ffmpeg","-y",
        "-f","concat",
        "-safe","0",
        "-i",list_path,
        "-c","copy",
        FINAL_OUTPUT
    ], check=True, capture_output=True)

    print(f"\n✨ SUCCESS! FINAL VIDEO: {FINAL_OUTPUT}")

# =========================================================
# MAIN
# =========================================================

async def run_engine():
    scenes = update_scene_durations_from_audio()
    outputs = []

    for i, scene in enumerate(scenes, 1):
        out = await process_scene(scene, i)
        if out:
            outputs.append(out)

    merge_all(outputs)

if __name__ == "__main__":
    try:
        asyncio.run(run_engine())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")
