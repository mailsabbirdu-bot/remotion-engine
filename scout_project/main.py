# =========================================================
# COUNTERISM AUDIO-FIRST RENDER ENGINE (COLAB OPTIMIZED)
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
import glob

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
    print("🧹 CLEARING OLD RENDS & TEMP FILES...")
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    if os.path.exists(RENDER_DIR):
        for f in os.listdir(RENDER_DIR):
            fpath = os.path.join(RENDER_DIR, f)
            try:
                if os.path.isfile(fpath): os.remove(fpath)
            except: pass

    if os.path.exists(FINAL_OUTPUT):
        os.remove(FINAL_OUTPUT)

cleanup()

START_PADDING = 0.5
END_PADDING = 0.5

# =========================================================
# DYNAMIC SCENE GENERATION
# =========================================================

def generate_production_plan():
    print("\n🎙️ SCANNING AUDIO FILES FOR SCENE GENERATION...")

    # Find all SC_xx.wav files
    audio_files = sorted(glob.glob(os.path.join(AUDIO_DIR, "SC_[0-9][0-9].wav")))

    if not audio_files:
        print(f"❌ No audio files found in {AUDIO_DIR} matching SC_XX.wav pattern!")
        return []

    scenes = []

    for idx, audio_path in enumerate(audio_files, start=1):
        audio_name = os.path.basename(audio_path)

        # Calculate duration
        audio = AudioSegment.from_wav(audio_path)
        audio_duration = len(audio) / 1000.0
        final_duration = START_PADDING + audio_duration + END_PADDING

        # Scene blueprint
        scene = {
            "scene_id": f"scene_{idx}",
            "text": "cinematic nature ocean atmosphere", # Default prompt if none provided
            "duration": round(final_duration, 2),
            "audio_path": audio_path,
            "audio_duration": round(audio_duration, 2),
            "audio_start_in_scene": START_PADDING,
            "asset_preferences": {
                "allow_video": True,
                "allow_image": True,
                "preferred_type": "video"
            },
            "scout_config": {
                "keywords": ["cinematic nature", "4k background"],
                "must_have_required": [],
                "must_have_optional": []
            }
        }
        scenes.append(scene)
        print(f"✅ Scene {idx}: {audio_name} → {round(final_duration, 2)}s")

    # Update the production plan file
    plan_data = {
        "project_name": "Dynamic_Project",
        "version": "COLAB_AUTO_V1",
        "scenes": scenes
    }

    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(plan_data, f, indent=2, ensure_ascii=False)

    print(f"📄 Production plan updated at: {PLAN_PATH}")
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
# RENDER VIDEO
# =========================================================

def render_scene_video(video, audio, out, duration, delay):
    temp_v = "/tmp/temp_v.mp4"

    # Step 1: Scale and Loop Video
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

    # Step 2: Mux Audio
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

# =========================================================
# PROCESS SCENE
# =========================================================

async def process_scene(scene, idx):
    print(f"\n🎬 RENDERING SCENE {idx}: {scene['scene_id']}")

    candidates = await get_all_candidates(scene)
    if not candidates:
        print("❌ NO ASSETS FOUND")
        return None

    best = candidates[0]

    ext = ".mp4" if best["type"]=="video" else ".jpg"
    asset_path = f"{TEMP_DIR}/asset_{idx}{ext}"

    print(f"📥 Downloading: {best['source']} ({best['type']})")
    ok = await download_asset(best["url"], asset_path)
    if not ok: return None

    out = f"{RENDER_DIR}/scene_{idx}.mp4"

    try:
        render_scene_video(
            asset_path,
            scene["audio_path"],
            out,
            scene["duration"],
            scene["audio_start_in_scene"]
        )
        print(f"✅ Scene {idx} saved to: {out}")
        return out
    except Exception as e:
        print(f"❌ RENDER FAILED for Scene {idx}: {e}")
        return None

# =========================================================
# MAIN
# =========================================================

async def run_engine():
    scenes = generate_production_plan()
    if not scenes: return

    outputs = []
    for i, scene in enumerate(scenes, 1):
        out = await process_scene(scene, i)
        if out: outputs.append(out)

    print(f"\n✨ ALL SCENES PROCESSED. TOTAL: {len(outputs)}")

if __name__ == "__main__":
    asyncio.run(run_engine())
