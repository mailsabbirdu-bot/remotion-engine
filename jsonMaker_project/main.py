import os
import sys
import re
import json
import time
import wave
from core.browser_automator import BrowserAI

# Path discovery for Colab vs Local
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

AUDIO_DIR = os.path.join(BASE, "audio")
MANIFESTS_DIR = os.path.join(BASE, "manifests") # Scout project plan usually goes here in execution BASE

# Source files
SCRIPT_UPDATED = os.path.join(AUDIO_DIR, "script_updated.txt")
STORY_TXT = os.path.join(AUDIO_DIR, "story.txt")
JSON_PREP = os.path.join(AUDIO_DIR, "jsonPrallowed") # As specified by user
JSON_PREP_ALT = os.path.join(AUDIO_DIR, "jsonPrep.txt") # Fallback

# Target files in Repository (to be updated) - Using parent directory since we run from within jsonMaker_project
SCOUT_PLAN_PATH = "../scout_project/manifests/production_plan.json"
REMOTION_PLAN_PATH = "../remotion_project/src/master_remotion.json"

def read_file_content(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def get_audio_duration(scene_idx):
    """Fallback duration estimation if audio files aren't physically present yet."""
    audio_path = os.path.join(AUDIO_DIR, f"SC_{str(scene_idx).zfill(2)}.wav")
    if os.path.exists(audio_path):
        with wave.open(audio_path, 'rb') as f:
            frames = f.getnframes()
            rate = f.getframerate()
            return frames / float(rate)
    return 8.0 # Default fallback

def parse_scenes(content):
    """Splits content into scenes, returning a list of scene blocks."""
    if not content: return []
    # Pattern to match "Scene X" or "দৃশ্য X" at the start of a line
    pattern = r'(?m)^(?:Scene|দৃশ্য)\s*(?:[০-৯\d]+)'
    parts = re.split(pattern, content)
    # The first part is usually empty or intro text, discard it if it doesn't look like a scene
    return [p.strip() for p in parts if p.strip()]

def extract_json(response):
    """Extracts a JSON object from AI response strings with extreme robustness."""
    if not response: return None

    # Pre-cleaning
    json_str = response.strip()
    # Remove markdown code blocks
    json_str = re.sub(r'^```json\s*', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'^```\s*', '', json_str, flags=re.MULTILINE)
    json_str = re.sub(r'\s*```$', '', json_str, flags=re.MULTILINE)

    # Find boundaries
    start_idx = json_str.find('{')
    end_idx = json_str.rfind('}')
    if start_idx == -1: return None
    json_str = json_str[start_idx : (end_idx+1 if end_idx != -1 else len(json_str))]

    # Fix common AI JSON errors
    # 1. Missing commas between properties/items
    json_str = re.sub(r'\}\s*\{', '}, {', json_str)
    json_str = re.sub(r'\]\s*\{', '], {', json_str)
    json_str = re.sub(r'\"\s*\"', '", "', json_str)

    # 2. Trailing commas
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)

    def balance_braces(s):
        diff_b = s.count('{') - s.count('}')
        diff_s = s.count('[') - s.count(']')
        if diff_s > 0: s += ']' * diff_s
        if diff_b > 0: s += '}' * diff_b
        return s

    try:
        return json.loads(json_str)
    except:
        try:
            # Attempt brace balancing
            return json.loads(balance_braces(json_str))
        except Exception as e:
            print(f"   ❌ Final Parse Error: {str(e)[:50]}")
            return None

def main():
    print("🚀 [JSON_MAKER] Starting Engine (SCENE-BY-SCENE MODE)...")

    # Ensure target directories exist
    for path in [SCOUT_PLAN_PATH, REMOTION_PLAN_PATH]:
        dir_name = os.path.dirname(path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)

    script_content = read_file_content(SCRIPT_UPDATED)
    story_content = read_file_content(STORY_TXT)
    prep_content = read_file_content(JSON_PREP) or read_file_content(JSON_PREP_ALT)

    if not all([script_content, story_content, prep_content]):
        print(f"❌ Error: Missing input files in {AUDIO_DIR}")
        sys.exit(1)

    # Read existing JSON templates with safety defaults
    try:
        with open(SCOUT_PLAN_PATH, "r", encoding="utf-8") as f:
            scout_template = json.load(f)
    except Exception:
        scout_template = {"project_name": "Dynamic_Project", "scenes": []}

    try:
        with open(REMOTION_PLAN_PATH, "r", encoding="utf-8") as f:
            remotion_template = json.load(f)
    except Exception:
        remotion_template = {"width": 1080, "height": 1920, "fps": 30, "scenes": []}

    # Detect language
    is_bn = bool(re.search(r'[\u0980-\u09ff]', story_content))
    target_lang = "Bengali (Bangla)" if is_bn else "English"

    # Parse into scenes
    story_scenes = parse_scenes(story_content)
    prep_scenes = parse_scenes(prep_content)

    num_scenes = max(len(story_scenes), len(prep_scenes))
    print(f"📋 Detected {num_scenes} scenes. Processing...")

    # Initialize Browser AI
    browser_ai = BrowserAI(headless=True)
    browser_ai.start()

    # Detect Topic from script_content
    topic_match = re.search(r"TOPIC:\s*(.*)", script_content)
    project_topic = topic_match.group(1).strip() if topic_match else "Cinematic Documentary"

    final_scout_scenes = []
    final_remotion_scenes = []

    batch_size = 6
    for i in range(0, num_scenes, batch_size):
        batch_end = min(i + batch_size, num_scenes)
        print(f"🎬 Processing scenes {i+1}-{batch_end}/{num_scenes}...")

        batch_story = story_scenes[i:batch_end]
        batch_prep = prep_scenes[i:batch_end]

        batch_input_str = ""
        for j, (s, p) in enumerate(zip(batch_story, batch_prep)):
            batch_input_str += f"S{i+j+1}: N: {s} | P: {p}\n"

        prompt = f"""Expert Video Producer. Generate JSON for scenes {i+1}-{batch_end} of "{project_topic}". Lang: {target_lang}.
Output MUST be raw JSON matching this structure perfectly. Use double quotes for all strings. Ensure all commas are correct.

{{
  "scenes": [
    {{
      "scout": {{
        "scene_id": "scene_{i+1}",
        "text": "Detailed cinematic visual description",
        "duration": [audio_duration + 1.0],
        "audio_path": "/content/drive/MyDrive/Counterism_Studio_V4/audio/SC_{str(i+1).zfill(2)}.wav",
        "audio_duration": [narration duration in seconds],
        "audio_start_in_scene": 0.5,
        "negative_prompts": ["text", "watermark", "blurry"],
        "asset_preferences": {{"allow_video": true, "allow_image": true, "preferred_type": "video"}},
        "scout_config": {{"keywords": ["keyword 1", "keyword 2"], "must_have_required": ["subject"], "must_have_optional": []}}
      }},
      "remotion": {{
        "id": "scene_{i+1}",
        "duration": [Float: duration_in_seconds * 30],
        "background": {{"type": "video", "src": "scene_{i+1}.mp4", "audio": ""}},
        "transition": {{"type": "fade", "duration": 15}},
        "layers": [{{
            "id": "l{i+1}", "type": "text", "content": "[Short hook from VISUAL PREP]", "start": 15, "duration": [frames],
            "style": {{"fontSize": 60, "color": "#ffffff", "x": 540, "y": 1550}},
            "animationIn": {{"type": "fade-up", "duration": 20}},
            "animationOut": {{"type": "fade-down", "duration": 20}},
            "textAnimation": {{"mode": "word", "duration": 40}},
            "textbox": {{"enabled": true, "type": "rounded-rect", "padding": 30, "fill": "rgba(0,0,0,0.60)"}},
            "keyframes": [{{"frame": 0, "scale": 1, "opacity": 0}}, {{"frame": 30, "scale": 1.05, "opacity": 1}}]
        }}]
      }}
    }}
  ]
}}

INPUT:
{batch_input_str}

STRICT: Return raw JSON only. Keywords must be excellent for Pixabay/Pexels search.
"""

        # Retry logic for individual batches
        data = None
        for attempt in range(2):
            # Speed optimization: smaller wait_time, sufficient timeout
            response = browser_ai.send_prompt(prompt, wait_time=3, timeout=150)
            data = extract_json(response) if response else None
            if data and "scenes" in data and len(data["scenes"]) > 0:
                break
            print(f"   ⚠️ Batch attempt {attempt+1} failed. Retrying...")
            browser_ai.new_chat() # Fresh start on failure
            time.sleep(1)

        if data and "scenes" in data:
            for scene_data in data["scenes"]:
                final_scout_scenes.append(scene_data["scout"])
                final_remotion_scenes.append(scene_data["remotion"])
            print(f"   ✅ Batch processed ({len(data['scenes'])} scenes).")
        else:
            print(f"   ❌ Batch {i//batch_size + 1} failed after retries. Using safety fallbacks for batch.")
            # Safety fallback for the entire batch
            for k in range(i, batch_end):
                scene_id = f"scene_{k+1}"
                fallback_duration_s = 7.0
                fallback_duration_f = 210
                final_scout_scenes.append({
                    "scene_id": scene_id,
                    "text": "cinematic atmosphere",
                    "duration": fallback_duration_s,
                    "audio_path": f"/content/drive/MyDrive/Counterism_Studio_V4/audio/SC_{str(k+1).zfill(2)}.wav",
                    "audio_duration": fallback_duration_s - 1.0,
                    "audio_start_in_scene": 0.5,
                    "negative_prompts": ["low quality"],
                    "asset_preferences": {"allow_video": True, "allow_image": True, "preferred_type": "video"},
                    "scout_config": {"keywords": ["cinematic"], "must_have_required": [], "must_have_optional": []}
                })
                final_remotion_scenes.append({
                    "id": scene_id,
                    "duration": fallback_duration_f,
                    "background": {"type": "video", "src": f"{scene_id}.mp4", "audio": ""},
                    "transition": {"type": "fade", "duration": 15},
                    "layers": [{
                        "id": f"l{k+1}", "type": "text", "content": "...", "start": 15, "duration": fallback_duration_f - 30,
                        "style": {"fontSize": 60, "color": "#ffffff", "x": 540, "y": 1550},
                        "animationIn": {"type": "fade-up", "duration": 20}, "animationOut": {"type": "fade-down", "duration": 20},
                        "textAnimation": {"mode": "word", "duration": 40},
                        "textbox": {"enabled": True, "type": "rounded-rect", "padding": 30, "fill": "rgba(0,0,0,0.60)"}
                    }]
                })

    # Reconstruct final JSONs
    scout_final = {
        "project_name": scout_template.get("project_name", "Dynamic_Project"),
        "version": "PRO_V1",
        "scenes": final_scout_scenes
    }

    remotion_final = {
        "width": remotion_template.get("width", 1080),
        "height": remotion_template.get("height", 1920),
        "fps": remotion_template.get("fps", 30),
        "banglaFont": remotion_template.get("banglaFont", "FN Mahin Dui Dashok Italic"),
        "englishFont": remotion_template.get("englishFont", "Audiowide-Regular"),
        "scenes": final_remotion_scenes
    }

    # Save to Repository
    with open(SCOUT_PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(scout_final, f, indent=2, ensure_ascii=False)
    print(f"✨ Updated Repository: {SCOUT_PLAN_PATH}")

    with open(REMOTION_PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(remotion_final, f, indent=2, ensure_ascii=False)
    print(f"✨ Updated Repository: {REMOTION_PLAN_PATH}")

    # Save to Google Drive (Execution Base) for immediate production use
    DRIVE_SCOUT = os.path.join(BASE, "manifests", "production_plan.json")
    DRIVE_REMOTION = os.path.join(BASE, "master_remotion.json")

    os.makedirs(os.path.dirname(DRIVE_SCOUT), exist_ok=True)

    with open(DRIVE_SCOUT, "w", encoding="utf-8") as f:
        json.dump(scout_final, f, indent=2, ensure_ascii=False)
    print(f"📂 Sync'd to Drive: {DRIVE_SCOUT}")

    with open(DRIVE_REMOTION, "w", encoding="utf-8") as f:
        json.dump(remotion_final, f, indent=2, ensure_ascii=False)
    print(f"📂 Sync'd to Drive: {DRIVE_REMOTION}")

    browser_ai.close()
    print("🎉 ALL SCENES PROCESSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
