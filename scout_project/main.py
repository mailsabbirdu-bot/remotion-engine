# =========================================================
# COUNTERISM AUDIO-FIRST RENDER ENGINE (PRO V4.1 - ULTIMATE)
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
import re
from PIL import Image

from pydub import AudioSegment
from core.scout import get_all_candidates
from core.technical_filter import technical_filter
from core.semantic_filter import semantic_filter
from core.vision_auditor import VisionAuditor
from core.model_manager import DEVICE

# Path discovery for Colab vs Local
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

# Manifest Template from Repository (Using absolute path discovery)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_PLAN_PATH = os.path.join(SCRIPT_DIR, "manifests", "production_plan.json")

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
print(f"📂 REPO TEMPLATE: {TEMPLATE_PLAN_PATH}")
print(f"⚡ HARDWARE ACCELERATION: {DEVICE.upper()}")

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
            fps = cap.get(cv2.CAP_PROP_FPS)
            total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
            if fps > 0:
                # Sample at 1.0s or middle if very short
                sample_frame = min(int(fps * 1.0), int(total * 0.5))
                cap.set(cv2.CAP_PROP_POS_FRAMES, sample_frame)

            ret, frame = cap.read()
            if not ret:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
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
    if os.path.exists(TEMPLATE_PLAN_PATH):
        print(f"📖 Template loaded from: {TEMPLATE_PLAN_PATH}")
        with open(TEMPLATE_PLAN_PATH, "r", encoding="utf-8") as f:
            template_data = json.load(f)
            template_scenes = template_data.get("scenes", [])
            project_name = template_data.get("project_name", "Dynamic_Project")
    else:
        print(f"⚠️ Template NOT found at {TEMPLATE_PLAN_PATH}. Using defaults.")
        template_scenes = []
        project_name = "Dynamic_Project"

    # Find ALL .wav files in audio folder (Flexible Naming Support)
    audio_files = sorted(glob.glob(os.path.join(AUDIO_DIR, "*.wav")) + glob.glob(os.path.join(AUDIO_DIR, "*.WAV")))
    if not audio_files:
        print(f"❌ No audio files found in {AUDIO_DIR}!")
        return []

    print(f"🔍 Found {len(audio_files)} audio files: {[os.path.basename(f) for f in audio_files]}")

    scenes = []
    for idx, audio_path in enumerate(audio_files):
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        txt_path = os.path.join(AUDIO_DIR, f"{base_name}.txt")

        # Determine Text Prompt
        story_text = ""
        if os.path.exists(txt_path):
            try:
                with open(txt_path, "r", encoding="utf-8") as f:
                    story_text = f.read().strip()
            except: pass

        # Calculate duration
        try:
            audio = AudioSegment.from_wav(audio_path)
            audio_duration = len(audio) / 1000.0
        except:
            audio_duration = 5.0
        final_duration = START_PADDING + audio_duration + END_PADDING

        # Initialize defaults
        text = story_text or "cinematic atmosphere"
        negative_prompts = ["low quality", "blurry", "text", "watermark", "people"]
        asset_preferences = {"allow_video": True, "allow_image": True, "preferred_type": "video"}
        scout_config = {"keywords": [], "must_have_required": [], "must_have_optional": []}

        # Apply template if available (matched by index)
        if idx < len(template_scenes):
            scene_template = template_scenes[idx]
            text = story_text or scene_template.get("text", text)
            negative_prompts = scene_template.get("negative_prompts", negative_prompts)
            asset_preferences = scene_template.get("asset_preferences", asset_preferences)
            scout_config = scene_template.get("scout_config", scout_config)

        # Smart Keyword Extraction from Story
        if story_text:
            words = re.findall(r'\w+', story_text.lower())
            stop_words = {'the', 'was', 'and', 'with', 'there', 'from', 'this', 'that', 'they', 'a', 'in', 'of', 'to'}
            unique_words = []
            seen = set()
            for w in words:
                if w not in seen and len(w) > 4 and w not in stop_words:
                    unique_words.append(w)
                    seen.add(w)
                if len(unique_words) >= 10: break

            # Use story keywords if template keywords are missing or generic
            current_keys = scout_config.get("keywords", [])
            if not current_keys or "ocean" in str(current_keys) or "cinematic" == str(current_keys):
                if len(unique_words) >= 3:
                    scout_config["keywords"] = [" ".join(unique_words[:3]), " ".join(unique_words[3:6])]
                else:
                    scout_config["keywords"] = [story_text[:50]]

        scene = {
            "scene_id": f"scene_{base_name}",
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
        print(f"✅ Scene {idx+1}: {os.path.basename(audio_path)} → {round(final_duration, 2)}s | Keywords: {scene['scout_config']['keywords']}")

    plan_data = {"project_name": project_name, "version": "PRO_V4_ULTIMATE", "scenes": scenes}
    with open(PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(plan_data, f, indent=2, ensure_ascii=False)

    print(f"📄 Production plan generated at: {PLAN_PATH}")
    return scenes

# =========================================================
# PARALLEL DOWNLOAD
# =========================================================

async def download_asset(session, url, path):
    try:
        async with session.get(url, timeout=30) as r:
            if r.status != 200: return None
            with open(path, "wb") as f:
                f.write(await r.read())
        return path
    except:
        return None

# =========================================================
# RENDER VIDEO
# =========================================================

def render_scene_video(asset_path, asset_type, audio, out, duration, delay):
    temp_v = os.path.join(TEMP_DIR, "temp_v_visual.mp4")
    if asset_type == "video":
        subprocess.run(["ffmpeg","-y", "-stream_loop","-1", "-i",asset_path, "-t",str(duration), "-vf","scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1", "-r","24", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "superfast", "-an", temp_v], check=True, capture_output=True)
    else:
        subprocess.run(["ffmpeg","-y", "-loop","1", "-i",asset_path, "-t",str(duration), "-vf","scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1", "-r","24", "-pix_fmt", "yuv420p", "-c:v", "libx264", "-preset", "superfast", "-an", temp_v], check=True, capture_output=True)
    subprocess.run(["ffmpeg","-y", "-i",temp_v, "-itsoffset",str(delay), "-i",audio, "-map","0:v:0", "-map","1:a:0", "-c:v","copy", "-c:a","aac", "-b:a", "128k", "-t",str(duration), out], check=True, capture_output=True)

# =========================================================
# PROCESS SCENE (WITH BATCH AUDIT)
# =========================================================

async def process_scene(scene, idx):
    print(f"\n🎬 [ENGINE] PROCESSING SCENE {idx}: {scene['scene_id']}")
    candidates = await get_all_candidates(scene)
    if not candidates: return None

    # Technical Filter handles 2K+ requirement
    candidates = technical_filter(candidates, scene["duration"])
    candidates = semantic_filter(scene, candidates)
    if not candidates: return None

    # 1. Parallel Download for Top 5
    top_candidates = candidates[:5]
    trial_data = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i, cand in enumerate(top_candidates, 1):
            ext = ".mp4" if cand["type"]=="video" else ".jpg"
            path = f"{TEMP_DIR}/scene_{idx}_trial_{i}{ext}"
            tasks.append(download_asset(session, cand["url"], path))
        paths = await asyncio.gather(*tasks)

        for cand, path in zip(top_candidates, paths):
            if path: trial_data.append((path, cand["type"]=="video", cand))

    if not trial_data: return None

    # 2. Batch Vision Audit (Speed Optimized)
    print(f"🔍 [ENGINE] Batch Auditing {len(trial_data)} candidates...")
    auditor = VisionAuditor(scene)
    audit_results = auditor.audit_batch(trial_data)

    final_selection = None
    asset_path = None

    for (path, is_vid, cand), result in zip(trial_data, audit_results):
        if not result: continue

        # Uniqueness Check
        v_hash = get_visual_hash(path, is_vid)
        if v_hash in HASH_REGISTRY:
            print(f"      ⚠️ [ENGINE] DUPLICATE DETECTED. Skipping...")
            continue

        print(f"      📊 Candidate {cand['source']}: Res={cand.get('width','?')}x{cand.get('height','?')} | Tech={cand.get('technical_score',0):.1f} | Sem={cand.get('semantic_score',0):.1f} | Vision={result['audit_score']}")

        if result["audit_score"] < 0:
            print(f"      ❌ [ENGINE] Visual mismatch. Skipping...")
            continue

        HASH_REGISTRY.add(v_hash)
        final_selection = cand
        asset_path = f"{TEMP_DIR}/scene_{idx}_final{os.path.splitext(path)[1]}"
        shutil.move(path, asset_path)
        print(f"      ✨ [ENGINE] UNIQUE ASSET SELECTED: {cand['source']} ({v_hash})")
        break

    if not final_selection:
        print("⚠️ [ENGINE] No unique/passing candidate in batch. Falling back.")
        path, is_vid, final_selection = trial_data[0]
        asset_path = f"{TEMP_DIR}/scene_{idx}_final{os.path.splitext(path)[1]}"
        shutil.move(path, asset_path)

    out = f"{RENDER_DIR}/{scene['scene_id']}.mp4"
    try:
        render_scene_video(asset_path, final_selection["type"], scene["audio_path"], out, scene["duration"], scene["audio_start_in_scene"])
        print(f"✅ [ENGINE] Scene {idx} saved: {os.path.basename(out)}")
        return out
    except Exception as e:
        print(f"❌ [ENGINE] RENDER FAILED: {e}")
        return None

async def run_engine():
    scenes = generate_production_plan()
    if not scenes: return
    if not shutil.which("ffmpeg"):
        print("❌ FFMPEG NOT FOUND. EXITING.")
        return
    for i, scene in enumerate(scenes, 1):
        await process_scene(scene, i)
    print(f"\n✨ ALL SCENES COMPLETED. CHECK RENDERS AT: {RENDER_DIR}")

if __name__ == "__main__":
    asyncio.run(run_engine())
