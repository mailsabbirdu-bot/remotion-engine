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
from core.semantic_filter import semantic_filter
from core.technical_filter import technical_filter

# Path discovery for Colab vs Local
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

# IMPORTANT: Initial plan comes from GITHUB/Local clone, then updated in Drive
REPO_PLAN_PATH = "manifests/production_plan.json"
DRIVE_PLAN_PATH = f"{BASE}/manifests/production_plan.json"

TEMP_DIR = "/content/temp_assets" if os.path.exists("/content") else "./temp_assets"
RENDER_DIR = f"{BASE}/renders"
FINAL_OUTPUT = f"{BASE}/final_video.mp4"
AUDIO_DIR = f"{BASE}/audio"

os.makedirs(RENDER_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DRIVE_PLAN_PATH), exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)

print(f"🚀 ENGINE STARTING. BASE: {BASE}")

def cleanup():
    print("🧹 CLEARING TEMP FILES...")
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

    # We clear RENDER_DIR but keep the folder
    if os.path.exists(RENDER_DIR):
        for f in os.listdir(RENDER_DIR):
            fpath = os.path.join(RENDER_DIR, f)
            try:
                if os.path.isfile(fpath): os.remove(fpath)
            except: pass

cleanup()

START_PADDING = 0.5
END_PADDING = 0.5

# =========================================================
# DYNAMIC SCENE GENERATION & PLAN SYNC
# =========================================================

def sync_and_generate_plan():
    print("\n🎙️ SYNCING PLAN WITH AUDIO FILES...")

    # Load base instructions from Repo
    if os.path.exists(REPO_PLAN_PATH):
        with open(REPO_PLAN_PATH, "r", encoding="utf-8") as f:
            base_data = json.load(f)
    else:
        print("⚠️ Base production_plan.json not found in repo! Creating empty plan.")
        base_data = {"scenes": []}

    audio_files = sorted(glob.glob(os.path.join(AUDIO_DIR, "SC_[0-9][0-9].wav")))

    if not audio_files:
        print(f"❌ No audio files found in {AUDIO_DIR}!")
        return []

    scenes = base_data.get("scenes", [])
    updated_scenes = []

    for idx, audio_path in enumerate(audio_files, start=1):
        # Find existing scene instruction or use default
        scene_id = f"scene_{idx}"
        existing = next((s for s in scenes if s["scene_id"] == scene_id), {})

        # Calculate duration
        audio = AudioSegment.from_wav(audio_path)
        audio_duration = len(audio) / 1000.0
        final_duration = START_PADDING + audio_duration + END_PADDING

        # Merge repo instructions with dynamic audio data
        scene = {
            "scene_id": scene_id,
            "text": existing.get("text", "cinematic nature atmosphere"),
            "negative_prompts": existing.get("negative_prompts", ["text", "watermark", "blurry"]),
            "duration": round(final_duration, 2),
            "audio_path": audio_path,
            "audio_duration": round(audio_duration, 2),
            "audio_start_in_scene": START_PADDING,
            "asset_preferences": existing.get("asset_preferences", {
                "allow_video": True, "allow_image": True, "preferred_type": "video"
            }),
            "scout_config": existing.get("scout_config", {
                "keywords": ["cinematic atmosphere"], "must_have_required": [], "must_have_optional": []
            })
        }
        updated_scenes.append(scene)
        print(f"✅ Synced Scene {idx}: {os.path.basename(audio_path)} → {round(final_duration, 2)}s")

    # Update Drive plan
    plan_data = {
        "project_name": base_data.get("project_name", "Automated_Project"),
        "version": "SCOUT_V2",
        "scenes": updated_scenes
    }

    with open(DRIVE_PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(plan_data, f, indent=2, ensure_ascii=False)

    return updated_scenes

# =========================================================
# DOWNLOAD
# =========================================================

async def download_asset(url, path):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=30) as r:
                if r.status != 200: return False
                with open(path, "wb") as f: f.write(await r.read())
        return True
    except: return False

# =========================================================
# RENDER VIDEO
# =========================================================

def render_scene_video(asset, audio, out, duration, delay):
    temp_v = "/tmp/temp_v.mp4"

    # Process Video/Image through FFmpeg
    # If image, we loop it for the duration. If video, we loop it too.
    input_flag = "-loop 1" if asset.endswith((".jpg", ".jpeg", ".png")) else "-stream_loop -1"

    subprocess.run([
        "ffmpeg","-y",
        *input_flag.split(), "-i", asset,
        "-t", str(duration),
        "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1",
        "-r", "24", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "superfast", "-an",
        temp_v
    ], check=True, capture_output=True)

    # Mux Audio
    subprocess.run([
        "ffmpeg","-y",
        "-i", temp_v,
        "-itsoffset", str(delay), "-i", audio,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest",
        out
    ], check=True, capture_output=True)

# =========================================================
# PROCESS SCENE
# =========================================================

async def process_scene(scene, idx):
    print(f"\n🎬 SCOUTING SCENE {idx}: {scene['scene_id']}")
    print(f"🔎 Query: {scene['text']}")

    # 1. Fetch Candidates
    candidates = await get_all_candidates(scene)
    if not candidates:
        print("❌ No candidates found.")
        return None

    # 2. Technical Filtering
    candidates = technical_filter(candidates, scene["duration"])

    # 3. Semantic Filtering (Selecting Best Match)
    candidates = semantic_filter(scene, candidates)

    if not candidates:
        print("❌ No suitable assets survived filtering.")
        return None

    best = candidates[0]
    print(f"🏆 BEST MATCH: {best['source']} - Score: {round(best.get('semantic_score',0), 3)}")

    ext = ".mp4" if best["type"]=="video" else ".jpg"
    asset_path = f"{TEMP_DIR}/asset_{idx}{ext}"

    # Download
    ok = await download_asset(best["url"], asset_path)
    if not ok: return None

    # Render
    out = f"{RENDER_DIR}/scene_{idx}.mp4"
    try:
        render_scene_video(asset_path, scene["audio_path"], out, scene["duration"], scene["audio_start_in_scene"])
        print(f"✅ Rendered: {out}")
        return out
    except Exception as e:
        print(f"❌ Render Error: {e}")
        return None

# =========================================================
# MAIN
# =========================================================

async def run_engine():
    scenes = sync_and_generate_plan()
    if not scenes: return

    for i, scene in enumerate(scenes, 1):
        await process_scene(scene, i)

    print(f"\n✨ ALL SCENES FINISHED. Renders available in: {RENDER_DIR}")

if __name__ == "__main__":
    asyncio.run(run_engine())
