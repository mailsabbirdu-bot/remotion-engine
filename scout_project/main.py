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
import cv2
import imagehash
from PIL import Image

from pydub import AudioSegment
from core.scout import get_all_candidates
from core.technical_filter import technical_filter
from core.semantic_filter import semantic_filter

# Path discovery for Colab vs Local
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

# Manifest Template from Repository
TEMPLATE_PLAN_PATH = "scout_project/manifests/production_plan.json"
# Updated plan goes to the execution BASE
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

# Visual Hash Registry to prevent duplicate footage
HASH_REGISTRY = set()

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
# VISUAL HASHING
# =========================================================

def get_visual_hash(path, is_video=True):
    try:
        if is_video:
            cap = cv2.VideoCapture(path)
            ret, frame = cap.read()
            cap.release()
            if not ret: return None
            img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        else:
            img = Image.open(path)

        return str(imagehash.phash(img))
    except:
        return None

# =========================================================
# DYNAMIC SCENE GENERATION
# =========================================================

def generate_production_plan():
    print("\n🎙️ SCANNING AUDIO FILES FOR SCENE GENERATION...")

    # Load Template from repository
    if os.path.exists(TEMPLATE_PLAN_PATH):
        with open(TEMPLATE_PLAN_PATH, "r", encoding="utf-8") as f:
            template_data = json.load(f)
            template_scenes = template_data.get("scenes", [])
            project_name = template_data.get("project_name", "Dynamic_Project")
    else:
        print(f"⚠️ Template not found at {TEMPLATE_PLAN_PATH}. Using generic setup.")
        template_scenes = []
        project_name = "Dynamic_Project"

    # Find all SC_xx.wav files in Drive/Local audio folder
    audio_files = sorted(glob.glob(os.path.join(AUDIO_DIR, "SC_[0-9][0-9].wav")))

    if not audio_files:
        print(f"❌ No audio files found in {AUDIO_DIR} matching SC_XX.wav pattern!")
        return []

    scenes = []

    for idx, audio_path in enumerate(audio_files):
        audio_name = os.path.basename(audio_path)

        # Calculate duration
        try:
            audio = AudioSegment.from_wav(audio_path)
            audio_duration = len(audio) / 1000.0
        except Exception as e:
            print(f"⚠️ Could not read audio {audio_name}, using default 5s: {e}")
            audio_duration = 5.0

        final_duration = START_PADDING + audio_duration + END_PADDING

        # Use template if available (matched by index)
        if idx < len(template_scenes):
            scene_template = template_scenes[idx]
            text = scene_template.get("text", "cinematic atmosphere")
            negative_prompts = scene_template.get("negative_prompts", ["low quality", "blurry"])
            asset_preferences = scene_template.get("asset_preferences", {
                "allow_video": True,
                "allow_image": True,
                "preferred_type": "video"
            })
            scout_config = scene_template.get("scout_config", {
                "keywords": ["cinematic"],
                "must_have_required": [],
                "must_have_optional": []
            })
        else:
            # Default fallback for extra audio files
            text = "cinematic atmosphere"
            negative_prompts = ["low quality", "blurry"]
            asset_preferences = {
                "allow_video": True,
                "allow_image": True,
                "preferred_type": "video"
            }
            scout_config = {
                "keywords": ["cinematic background"],
                "must_have_required": [],
                "must_have_optional": []
            }

        # Scene blueprint
        scene = {
            "scene_id": f"scene_{idx+1}",
            "text": text,
            "duration": round(final_duration, 2),
            "audio_path": audio_path,
            "audio_duration": round(audio_duration, 2),
            "audio_start_in_scene": START_PADDING,
            "negative_prompts": negative_prompts,
            "asset_preferences": asset_preferences,
            "scout_config": scout_config
        }
        scenes.append(scene)
        print(f"✅ Scene {idx+1}: {audio_name} → {round(final_duration, 2)}s")

    # Save the updated production plan for execution
    plan_data = {
        "project_name": project_name,
        "version": "REPO_TEMPLATE_V1",
        "scenes": scenes
    }

    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(plan_data, f, indent=2, ensure_ascii=False)

    print(f"📄 Production plan generated at: {PLAN_PATH}")
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

def render_scene_video(asset_path, asset_type, audio, out, duration, delay):
    temp_v = os.path.join(TEMP_DIR, "temp_v_visual.mp4")

    # Step 1: Process visual asset based on type
    if asset_type == "video":
        subprocess.run([
            "ffmpeg","-y",
            "-stream_loop","-1",
            "-i",asset_path,
            "-t",str(duration),
            "-vf","scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1",
            "-r","24",
            "-pix_fmt", "yuv420p",
            "-c:v", "libx264",
            "-preset", "superfast",
            "-an",
            temp_v
        ], check=True, capture_output=True)
    else:
        subprocess.run([
            "ffmpeg","-y",
            "-loop","1",
            "-i",asset_path,
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
        "-map","0:v:0",
        "-map","1:a:0",
        "-c:v","copy",
        "-c:a","aac",
        "-b:a", "128k",
        "-t",str(duration),
        out
    ], check=True, capture_output=True)

# =========================================================
# PROCESS SCENE
# =========================================================

async def process_scene(scene, idx):
    print(f"\n🎬 [ENGINE] PROCESSING SCENE {idx}: {scene['scene_id']}")

    # 1. Get raw candidates
    candidates = await get_all_candidates(scene)
    if not candidates:
        print("❌ [ENGINE] NO ASSETS FOUND")
        return None

    # 2. Apply Filters and Log Scores
    print(f"🔍 [ENGINE] Evaluating {len(candidates)} candidates...")
    candidates = technical_filter(candidates, scene["duration"])
    candidates = semantic_filter(scene, candidates)

    if not candidates:
        print("❌ [ENGINE] NO ASSETS SURVIVED FILTERING")
        return None

    # 3. Visual Deduplication (ImageHash)
    final_selection = None

    for rank, cand in enumerate(candidates, 1):
        ext = ".mp4" if cand["type"]=="video" else ".jpg"
        trial_path = f"{TEMP_DIR}/trial_{idx}_{rank}{ext}"

        print(f"📥 [ENGINE] Evaluating Candidate #{rank}: {cand['source']} ({cand['type']})")
        print(f"   📊 Tech Score: {cand.get('technical_score', 0):.2f} | Semantic Score: {cand.get('semantic_score', 0):.2f}")

        ok = await download_asset(cand["url"], trial_path)
        if not ok: continue

        v_hash = get_visual_hash(trial_path, cand["type"]=="video")
        if v_hash in HASH_REGISTRY:
            print(f"   ⚠️ [ENGINE] DUPLICATE DETECTED (Hash: {v_hash}). Skipping...")
            continue

        # Valid Unique Asset Found
        HASH_REGISTRY.add(v_hash)
        final_selection = cand
        asset_path = f"{TEMP_DIR}/asset_{idx}{ext}"
        os.rename(trial_path, asset_path)
        print(f"   ✨ [ENGINE] UNIQUE ASSET SELECTED (Hash: {v_hash})")
        break

    if not final_selection:
        print("❌ [ENGINE] NO UNIQUE ASSETS FOUND AMONG TOP CANDIDATES")
        return None

    out = f"{RENDER_DIR}/scene_{idx}.mp4"

    try:
        render_scene_video(
            asset_path,
            final_selection["type"],
            scene["audio_path"],
            out,
            scene["duration"],
            scene["audio_start_in_scene"]
        )
        print(f"✅ [ENGINE] Scene {idx} saved to: {out}")
        return out
    except Exception as e:
        print(f"❌ [ENGINE] RENDER FAILED for Scene {idx}: {e}")
        return None

# =========================================================
# MAIN
# =========================================================

async def run_engine():
    scenes = generate_production_plan()
    if not scenes: return

    if not shutil.which("ffmpeg"):
        print("⚠️ ffmpeg not found. Skipping rendering.")
        return

    outputs = []
    for i, scene in enumerate(scenes, 1):
        out = await process_scene(scene, i)
        if out: outputs.append(out)

    print(f"\n✨ ALL SCENES PROCESSED. TOTAL: {len(outputs)}")

if __name__ == "__main__":
    asyncio.run(run_engine())
