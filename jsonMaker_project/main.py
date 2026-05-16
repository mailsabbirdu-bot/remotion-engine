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

# Target files in Repository (to be updated)
# Determine if we are running from inside jsonMaker_project or from project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

SCOUT_PLAN_PATH = os.path.join(REPO_ROOT, "scout_project", "manifests", "production_plan.json")
REMOTION_PLAN_PATH = os.path.join(REPO_ROOT, "remotion_project", "src", "master_remotion.json")

# Adjust BASE for LOCAL_BASE to be relative to REPO_ROOT
LOCAL_BASE = os.path.join(REPO_ROOT, "Counterism_Studio_V4")

def read_file_content(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def get_audio_duration(scene_idx):
    """Calculates audio duration using pydub or wave."""
    audio_path = os.path.join(AUDIO_DIR, f"SC_{str(scene_idx).zfill(2)}.wav")

    # Try pydub first (handles more formats)
    try:
        from pydub import AudioSegment
        if os.path.exists(audio_path):
            audio = AudioSegment.from_file(audio_path)
            return len(audio) / 1000.0
    except:
        pass

    # Fallback to wave
    if os.path.exists(audio_path):
        try:
            with wave.open(audio_path, 'rb') as f:
                frames = f.getnframes()
                rate = f.getframerate()
                return frames / float(rate)
        except:
            pass

    return 8.0 # Default fallback if file missing or unreadable

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

    # Pre-cleaning: Remove potential non-JSON preamble/epilogue
    # Find the first '[' or '{' and the last ']' or '}'
    match = re.search(r'([\[\{].*[\]\}])', response, re.DOTALL)
    if not match:
        # Fallback to search for boundaries manually if regex fails on large strings
        start_idx = response.find('{')
        if start_idx == -1: start_idx = response.find('[')
        end_idx = response.rfind('}')
        if end_idx == -1: end_idx = response.rfind(']')
        if start_idx == -1 or end_idx == -1: return None
        json_str = response[start_idx:end_idx+1]
    else:
        json_str = match.group(1)

    # Remove markdown code blocks if still present
    json_str = re.sub(r'```json\s*', '', json_str)
    json_str = re.sub(r'```', '', json_str)

    # Fix common AI JSON errors
    # 1. Trailing commas before closing braces/brackets
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)

    # 2. Missing commas between objects or arrays
    json_str = re.sub(r'\}\s*\{', '}, {', json_str)
    json_str = re.sub(r'\]\s*\[', '], [', json_str)
    json_str = re.sub(r'\]\s*\{', '], {', json_str)

    # 3. Smart quote replacement
    json_str = json_str.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")

    def balance_json(s):
        """Attempts to balance braces and brackets."""
        braces = s.count('{') - s.count('}')
        brackets = s.count('[') - s.count(']')
        if brackets > 0: s += ']' * brackets
        if braces > 0: s += '}' * braces
        return s

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            return json.loads(balance_json(json_str))
        except Exception as e:
            # Last ditch effort: try to find the largest valid JSON block
            print(f"   ⚠️ Initial parse failed, attempting recovery...")
            try:
                # Try finding valid scenes array if it's a batch
                scenes_match = re.search(r'\"scenes\"\s*:\s*\[(.*)\]', json_str, re.DOTALL)
                if scenes_match:
                    inner_json = "[" + scenes_match.group(1) + "]"
                    # Attempt to parse each object in the array individually if the whole array fails
                    # This is complex, so we'll just try to fix the array string
                    inner_json = re.sub(r',\s*$', '', inner_json.strip())
                    if not inner_json.endswith(']'): inner_json += ']'
                    valid_scenes = json.loads(balance_json(inner_json))
                    return {"scenes": valid_scenes}
            except:
                pass
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

    # Parse into scenes
    story_scenes = parse_scenes(story_content)
    prep_scenes = parse_scenes(prep_content)

    num_scenes = max(len(story_scenes), len(prep_scenes))
    print(f"📋 Detected {num_scenes} scenes. Processing...")

    # Detect Topic and Language from script_content
    topic_match = re.search(r"TOPIC:\s*(.*)", script_content)
    project_topic = topic_match.group(1).strip() if topic_match else "Cinematic Documentary"

    # User requirement: detect language from TOPIC
    is_bn = bool(re.search(r'[\u0980-\u09ff]', project_topic))
    target_lang = "Bengali (Bangla)" if is_bn else "English"
    print(f"🌍 Detected Language: {target_lang}")

    # Initialize Browser AI
    browser_ai = BrowserAI(headless=True)
    browser_ai.start()

    final_scout_scenes = []
    final_remotion_scenes = []

    batch_size = 3  # Reduced for maximum quality and less truncation
    for i in range(0, num_scenes, batch_size):
        batch_end = min(i + batch_size, num_scenes)
        print(f"🎬 Processing scenes {i+1}-{batch_end}/{num_scenes}...")

        batch_story = story_scenes[i:batch_end]
        batch_prep = prep_scenes[i:batch_end]

        batch_input_str = ""
        for j in range(batch_end - i):
            idx = i + j + 1
            s = batch_story[j] if j < len(batch_story) else ""
            p = batch_prep[j] if j < len(batch_prep) else ""
            dur = get_audio_duration(idx)
            padded_num = str(idx).zfill(2)
            batch_input_str += f"### SCENE {idx} ###\n"
            batch_input_str += f"REQUIRED_ID: scene_SC_{padded_num}\n"
            batch_input_str += f"AUDIO_FILE: SC_{padded_num}.wav\n"
            batch_input_str += f"NARRATION_LENGTH: {dur:.2f}s\n"
            batch_input_str += f"NARRATION_TEXT: {s}\n"
            batch_input_str += f"VISUAL_PREP: {p}\n\n"

        prompt = f"""You are the Lead Video Production AI for Counterism Studio.
Your mission is to generate high-precision JSON metadata for a cinematic documentary.

TOPIC: "{project_topic}"
PRIMARY LANGUAGE: {target_lang}

STRICT INSTRUCTIONS FOR FIELDS:
1. SCOUT ENGINE (B-Roll Data):
   - `scout.text` and `scout.scout_config.keywords`: Use the `scout` field from `VISUAL_PREP`. ALWAYS USE ENGLISH.
   - Quality: Descriptions must be professional cinematographic prompts. Keywords must be excellent for stock footage search.
   - `duration`: audio_duration + 1.0.

2. REMOTION ENGINE (Overlay Data):
   - Use the specific values provided in `VISUAL_PREP` for `scout`, `Text`, `Textbox`, `Animation`, `Color`, and `Transition`.
   - `remotion.layers[0].content`: Use the `Text` field from `VISUAL_PREP`.
   - `remotion.layers[0].textbox.type`: Use the `Textbox` field from `VISUAL_PREP`.
   - `remotion.layers[0].animationIn.type` and `animationOut.type`: Extract from the `Animation` field in `VISUAL_PREP`.
   - `remotion.layers[0].style.color`: Use the `Text` color from the `Color` field in `VISUAL_PREP`.
   - `remotion.layers[0].textbox.fill`: Use the `Textbox` color from the `Color` field in `VISUAL_PREP`.
   - `remotion.transition.type`: Use the `Transition` field from `VISUAL_PREP`.
   - `duration`: total_duration * 30 (integer frames).

3. MATCH IDS & FILENAMES EXACTLY:
   - Follow the `REQUIRED_ID` and `AUDIO_FILE` provided for each scene.

OUTPUT MUST BE RAW JSON ONLY. NO PREAMBLE. NO CONVERSATION.

SCHEMA TEMPLATE (Generate exactly {batch_end - i} scenes):
{{
  "scenes": [
    {{
      "scout": {{
        "scene_id": "scene_SC_XX",
        "text": "English cinematic description",
        "duration": [audio_duration + 1.0],
        "audio_path": "/content/drive/MyDrive/Counterism_Studio_V4/audio/SC_XX.wav",
        "audio_duration": [Exact narration length provided],
        "audio_start_in_scene": 0.5,
        "negative_prompts": ["text", "watermark", "blurry"],
        "asset_preferences": {{"allow_video": true, "allow_image": true, "preferred_type": "video"}},
        "scout_config": {{"keywords": ["keyword 1", "keyword 2"], "must_have_required": [], "must_have_optional": []}}
      }},
      "remotion": {{
        "id": "scene_SC_XX",
        "duration": [frames],
        "background": {{"type": "video", "src": "scene_SC_XX.mp4", "audio": ""}},
        "transition": {{"type": "fade", "duration": 15}},
        "layers": [{{
            "id": "l1", "type": "text", "content": "[Hook in {target_lang}]",
            "start": 15, "duration": [frames - 30],
            "style": {{"fontSize": 65, "color": "#ffffff", "x": 540, "y": 1550}},
            "animationIn": {{"type": "fade-up", "duration": 20, "easing": "cubic-bezier(0.33, 1, 0.68, 1)"}},
            "animationOut": {{"type": "fade-down", "duration": 20}},
            "textAnimation": {{"mode": "word", "duration": 40}},
            "textbox": {{"enabled": true, "type": "rounded-rect", "padding": 35, "fill": "rgba(0,0,0,0.65)"}},
            "keyframes": [{{"frame": 0, "scale": 1, "opacity": 0}}, {{"frame": 25, "scale": 1.02, "opacity": 1}}]
        }}]
      }}
    }}
  ]
}}

INPUT DATA:
{batch_input_str}
"""

        # Retry logic for individual batches
        data = None
        expected_count = batch_end - i
        for attempt in range(2):
            # Speed optimization: smaller wait_time, sufficient timeout
            response = browser_ai.send_prompt(prompt, wait_time=3, timeout=150)
            data = extract_json(response) if response else None

            if data and "scenes" in data:
                received_count = len(data["scenes"])
                if received_count == expected_count:
                    break
                else:
                    print(f"   ⚠️ Batch scene count mismatch: Expected {expected_count}, got {received_count}.")

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
