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

# Manifest Template from Repository
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
            if fps > 0:
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(fps * 1.0))
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

def get_unique_words(story_text, limit=15):
    if not story_text: return []
    words = re.findall(r'\w+', story_text.lower())
    unique_words = []
    seen = set()
    for w in words:
        if w not in seen and len(w) > 2:
            unique_words.append(w)
            seen.add(w)
        if len(unique_words) >= limit: break
    return unique_words

def generate_production_plan():
    print("\n🎙️ SCANNING AUDIO FILES FOR SCENE GENERATION...")
    if os.path.exists(TEMPLATE_PLAN_PATH):
        with open(TEMPLATE_PLAN_PATH, "r", encoding="utf-8") as f:
            template_data = json.load(f)
            template_scenes = template_data.get("scenes", [])
            project_name = template_data.get("project_name", "Dynamic_Project")
    else:
        template_scenes = []
        project_name = "Dynamic_Project"

    # Find ALL .wav files in audio folder
    audio_files = sorted(glob.glob(os.path.join(AUDIO_DIR, "*.wav")))
    if not audio_files:
        print(f"❌ No audio files found in {AUDIO_DIR}!")
        return []

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
            except:
                pass

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

        # Dynamic Keyword Extraction from Story
        if story_text:
            unique_words = get_unique_words(story_text, limit=10)

            # If template keywords are generic or missing, use story keywords
            if not scout_config.get("keywords") or "ocean" in scout_config.get("keywords", [])[0]:
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

    plan_data = {"project_name": project_name, "version": "PRO_V3", "scenes": scenes}
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

    # 1. Initial Candidates Pool
    all_pool = await get_all_candidates(scene)
    if not all_pool: return None
    all_pool = technical_filter(all_pool, scene["duration"])
    all_pool = semantic_filter(scene, all_pool)

    audited_urls = set()
    is_strict = scene.get("strict_mode", False)
    must_have = scene.get("scout_config", {}).get("must_have_required", [])
    custom_detail = scene.get("custom_detail", "")

    final_selection = None
    asset_path = None
    scored_trials = []

    # Two Main Phases
    for phase in range(1, 3):
        if phase == 2:
            if not is_strict or (not must_have and not custom_detail): break
            print(f"🔄 [ENGINE] PHASE 2: Triggering EXTREME RE-SEARCH for mandatory items...")

            phase2_scene = scene.copy()
            phase2_scene["scout_config"] = scene["scout_config"].copy()

            # Focused searching
            keywords = []
            if custom_detail:
                keywords.append(custom_detail)
                keywords.append(f"{custom_detail} close up macro")
            if must_have:
                keywords.extend(must_have)
                for m in must_have:
                    keywords.append(f"{m} close up")

            phase2_scene["scout_config"]["keywords"] = keywords

            new_candidates = await get_all_candidates(phase2_scene)
            if new_candidates:
                new_candidates = technical_filter(new_candidates, scene["duration"])
                new_candidates = semantic_filter(phase2_scene, new_candidates)
                all_pool.extend([c for c in new_candidates if c["url"] not in [x["url"] for x in all_pool]])

        candidates = [c for c in all_pool if c["url"] not in audited_urls]
        if not candidates: continue

        batch_size = 12 if phase == 1 and is_strict else 8
        top_batch = candidates[:batch_size]

        trial_data = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i, cand in enumerate(top_batch, 1):
                ext = ".mp4" if cand["type"]=="video" else ".jpg"
                path = f"{TEMP_DIR}/scene_{idx}_p{phase}_t{i}{ext}"
                tasks.append(download_asset(session, cand["url"], path))
                audited_urls.add(cand["url"])
            paths = await asyncio.gather(*tasks)
            for cand, path in zip(top_batch, paths):
                if path: trial_data.append((path, cand["type"]=="video", cand))

        if not trial_data: continue

        print(f"🔍 [ENGINE] Batch Auditing {len(trial_data)} candidates (Phase {phase})...")
        auditor = VisionAuditor(scene)
        audit_results = auditor.audit_batch(trial_data)

        for (path, is_vid, cand), result in zip(trial_data, audit_results):
            if result:
                scored_trials.append(((path, is_vid, cand), result))

        scored_trials.sort(key=lambda x: x[1]["audit_score"], reverse=True)

        phase_match = False
        for (path, is_vid, cand), result in scored_trials:
            if not os.path.exists(path): continue
            v_hash = get_visual_hash(path, is_vid)
            if v_hash in HASH_REGISTRY: continue

            mandatory_str = " [MANDATORY MATCH]" if result.get("mandatory_match") else ""
            print(f"      📊 Candidate {cand['source']}: Audit={result['audit_score']:.1f}{mandatory_str} | Captions: {result.get('captions', [])}")

            if result["audit_score"] < 0: continue

            # Strict mode Phase 1 REQUIREMENT
            if is_strict and (must_have or custom_detail) and phase == 1 and not result.get("mandatory_match"):
                continue

            HASH_REGISTRY.add(v_hash)
            final_selection = cand
            asset_path = f"{TEMP_DIR}/scene_{idx}_final{os.path.splitext(path)[1]}"
            shutil.move(path, asset_path)
            print(f"      ✨ [ENGINE] UNIQUE ASSET SELECTED: {cand['source']} ({v_hash})")
            phase_match = True
            break

        if phase_match: break

    if not final_selection:
        print("⚠️ [ENGINE] No perfect candidate found. Falling back to highest scored trial.")
        if scored_trials:
            scored_trials.sort(key=lambda x: x[1]["audit_score"], reverse=True)
            (path, is_vid, final_selection), result = scored_trials[0]
            asset_path = f"{TEMP_DIR}/scene_{idx}_final{os.path.splitext(path)[1]}"
            if os.path.exists(path): shutil.move(path, asset_path)
        else: return None

    out = f"{RENDER_DIR}/{scene['scene_id']}.mp4"
    try:
        render_scene_video(asset_path, final_selection["type"], scene["audio_path"], out, scene["duration"], scene["audio_start_in_scene"])
        print(f"✅ [ENGINE] Scene {idx} saved to: {out}")
        return out
    except Exception as e:
        print(f"❌ [ENGINE] RENDER FAILED: {e}")
        return None

async def run_engine():
    scenes = generate_production_plan()
    if not scenes: return
    if not shutil.which("ffmpeg"): return
    for i, scene in enumerate(scenes, 1):
        await process_scene(scene, i)

if __name__ == "__main__":
    cleanup()
    asyncio.run(run_engine())
