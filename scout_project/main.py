# =========================================================
# COUNTERISM AUDIO-FIRST RENDER ENGINE (ULTIMATE FIXED)
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
from core.semantic_filter import semantic_filter
from core.technical_filter import technical_filter

# --- PATH CONFIGURATION ---
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

# Instructions come from GitHub, Results go to Drive
REPO_PLAN_PATH = os.path.abspath("manifests/production_plan.json")
DRIVE_PLAN_PATH = os.path.join(BASE, "manifests/production_plan.json")

# Using fast local storage for temp files
TEMP_DIR = "/content/temp_assets" if os.path.exists("/content") else "./temp_assets"
RENDER_DIR = os.path.join(BASE, "renders")
AUDIO_DIR = os.path.join(BASE, "audio")

os.makedirs(RENDER_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DRIVE_PLAN_PATH), exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

print(f"🚀 SCOUT ENGINE STARTING. BASE: {BASE}")

def cleanup():
    print("🧹 Cleaning temporary workspace...")
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Optional: Clear renders folder at start of each run
    if os.path.exists(RENDER_DIR):
        for f in os.listdir(RENDER_DIR):
            try: os.remove(os.path.join(RENDER_DIR, f))
            except: pass

cleanup()

START_PADDING = 0.5
END_PADDING = 0.5

# =========================================================
# INTELLIGENT PLAN GENERATION
# =========================================================

def sync_instructions_with_audio():
    print("\n🎙️ Matching GitHub instructions with Drive audio files...")

    # Load visual instructions (prompts, negative prompts) from Repo
    if os.path.exists(REPO_PLAN_PATH):
        with open(REPO_PLAN_PATH, "r", encoding="utf-8") as f:
            repo_data = json.load(f)
    else:
        print("⚠️ GitHub production_plan.json not found! Using generic prompts.")
        repo_data = {"scenes": []}

    # Detect all SC_XX.wav files in Drive
    audio_files = sorted(glob.glob(os.path.join(AUDIO_DIR, "SC_[0-9][0-9].wav")))

    if not audio_files:
        print(f"❌ Error: No SC_XX.wav files found in {AUDIO_DIR}!")
        return []

    repo_scenes = repo_data.get("scenes", [])
    synced_scenes = []

    for idx, audio_path in enumerate(audio_files, start=1):
        scene_id = f"scene_{idx}"
        # Try to find corresponding prompt in repo JSON
        instr = next((s for s in repo_scenes if s["scene_id"] == scene_id), {})

        # Calculate precise duration with padding
        audio = AudioSegment.from_wav(audio_path)
        audio_dur = len(audio) / 1000.0
        total_dur = START_PADDING + audio_dur + END_PADDING

        # Build the final scene blueprint
        scene = {
            "scene_id": scene_id,
            "text": instr.get("text", "cinematic landscape 4k"),
            "negative_prompts": instr.get("negative_prompts", ["text", "watermark", "blurry", "person"]),
            "duration": round(total_dur, 2),
            "audio_path": audio_path,
            "audio_duration": round(audio_dur, 2),
            "audio_start_in_scene": START_PADDING,
            "asset_preferences": instr.get("asset_preferences", {
                "allow_video": True, "allow_image": True, "preferred_type": "video"
            }),
            "scout_config": instr.get("scout_config", {
                "keywords": [instr.get("text", "cinematic")],
                "must_have_required": [],
                "must_have_optional": []
            })
        }
        synced_scenes.append(scene)
        print(f"✅ Scene {idx}: {os.path.basename(audio_path)} -> {round(total_dur, 2)}s")

    # Save the updated plan back to Drive for reference
    final_data = {
        "project_name": repo_data.get("project_name", "Auto_Render"),
        "timestamp": "latest",
        "scenes": synced_scenes
    }

    with open(DRIVE_PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    return synced_scenes

# =========================================================
# CORE RENDER LOGIC
# =========================================================

def render_scene_video(asset, audio, out, duration, delay):
    temp_v = "/tmp/temp_render_v.mp4"

    # Detect asset type
    is_img = asset.lower().endswith((".jpg", ".jpeg", ".png"))
    loop_flag = "-loop 1" if is_img else "-stream_loop -1"

    # 1. Scale and Loop to target duration
    subprocess.run([
        "ffmpeg", "-y",
        *loop_flag.split(), "-i", asset,
        "-t", str(duration),
        "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1",
        "-r", "24", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "superfast", "-an",
        temp_v
    ], check=True, capture_output=True)

    # 2. Mux Audio with Breathing Offset
    subprocess.run([
        "ffmpeg", "-y",
        "-i", temp_v,
        "-itsoffset", str(delay), "-i", audio,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
        out
    ], check=True, capture_output=True)

# =========================================================
# ASSET SELECTION & PROCESSING
# =========================================================

async def download_asset(url, path):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=40) as r:
                if r.status == 200:
                    with open(path, "wb") as f: f.write(await r.read())
                    return True
    except: pass
    return False

async def process_scene(scene, idx):
    print(f"\n🎬 PROCESSING SCENE {idx} ({scene['scene_id']})")

    # 1. Scout
    candidates = await get_all_candidates(scene)
    if not candidates: return None

    # 2. Match
    candidates = technical_filter(candidates, scene["duration"])
    candidates = semantic_filter(scene, candidates)

    if not candidates:
        print(f"❌ No suitable assets found for Scene {idx}")
        return None

    best = candidates[0]
    print(f"🏆 Best Candidate: {best['source']} | Score: {round(best.get('semantic_score',0), 3)}")

    ext = ".mp4" if best["type"]=="video" else ".jpg"
    asset_path = os.path.join(TEMP_DIR, f"asset_{idx}{ext}")

    # 3. Download & Render
    if await download_asset(best["url"], asset_path):
        out = os.path.join(RENDER_DIR, f"scene_{idx}.mp4")
        try:
            render_scene_video(asset_path, scene["audio_path"], out, scene["duration"], scene["audio_start_in_scene"])
            print(f"✨ Successfully rendered Scene {idx}")
            return out
        except Exception as e:
            print(f"❌ Render Error: {e}")
    return None

# =========================================================
# ENTRY POINT
# =========================================================

async def run_scout_engine():
    scenes = sync_instructions_with_audio()
    if not scenes: return

    for i, scene in enumerate(scenes, 1):
        await process_scene(scene, i)

    print(f"\n🏁 ALL TASKS COMPLETED. Scenes are in {RENDER_DIR}")

if __name__ == "__main__":
    asyncio.run(run_scout_engine())
