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
    """Extracts a JSON object from AI response strings."""
    json_str = response.strip()
    match = re.search(r'(\{.*\})', json_str, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].strip()

    # Basic truncation fix
    if not json_str.endswith("}"):
        open_braces = json_str.count("{")
        close_braces = json_str.count("}")
        if open_braces > close_braces:
            json_str += "}" * (open_braces - close_braces)

    try:
        return json.loads(json_str)
    except:
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

    # Read existing JSON templates
    with open(SCOUT_PLAN_PATH, "r", encoding="utf-8") as f:
        scout_template = json.load(f)
    with open(REMOTION_PLAN_PATH, "r", encoding="utf-8") as f:
        remotion_template = json.load(f)

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

    for i in range(num_scenes):
        scene_id = f"scene_{i+1}"
        print(f"🎬 Processing {scene_id}/{num_scenes}...")

        story_text = story_scenes[i] if i < len(story_scenes) else "..."
        prep_text = prep_scenes[i] if i < len(prep_scenes) else "..."

        prompt = f"""You are an expert video producer and JSON engineer. Generate two high-quality JSON fragments for Scene {i+1} of a documentary about: "{project_topic}".

TARGET LANGUAGE: {target_lang}

INPUT:
1. SCENE NARRATION:
{story_text}

2. VISUAL PREPARATION GUIDE:
{prep_text}

OUTPUT FORMAT (MANDATORY):
{{
  "scout_scene": {{
    "scene_id": "{scene_id}",
    "text": "Detailed visual description for stock footage search",
    "duration": [Float: audio_duration + 1.0],
    "audio_path": "/content/drive/MyDrive/Counterism_Studio_V4/audio/SC_{str(i+1).zfill(2)}.wav",
    "audio_duration": [Float: narration duration in seconds],
    "audio_start_in_scene": 0.5,
    "negative_prompts": ["low quality", "blurry", "text", "watermark", "ugly"],
    "asset_preferences": {{"allow_video": true, "allow_image": true, "preferred_type": "video"}},
    "scout_config": {{
      "keywords": ["pixabay search term 1", "pexels search term 2"],
      "must_have_required": ["core subject"],
      "must_have_optional": []
    }}
  }},
  "remotion_scene": {{
    "id": "{scene_id}",
    "duration": [Int: total duration in frames at 30fps. 1s=30frames],
    "background": {{"type": "video", "src": "{scene_id}.mp4", "audio": ""}},
    "transition": {{"type": "fade", "duration": 15}},
    "layers": [
      {{
        "id": "l{i+1}",
        "type": "text",
        "content": "[Hooky text from VISUAL PREP]",
        "start": 15,
        "duration": [Int: scene duration - 30],
        "style": {{"fontSize": 60, "color": "#ffffff", "x": 540, "y": 1550}},
        "animationIn": {{"type": "fade-up", "duration": 20, "easing": "cubic-bezier(0.33, 1, 0.68, 1)"}},
        "animationOut": {{"type": "fade-down", "duration": 20, "easing": "ease-in"}},
        "textAnimation": {{"mode": "word", "duration": 40}},
        "textbox": {{"enabled": true, "type": "rounded-rect", "padding": 30, "fill": "rgba(0,0,0,0.60)"}},
        "keyframes": [
           {{"frame": 0, "scale": 1, "opacity": 0}},
           {{"frame": 30, "scale": 1.05, "opacity": 1}}
        ]
      }}
    ]
  }}
}}

CRITICAL REQUIREMENTS:
1. SEARCH OPTIMIZATION: Keywords must be perfect for Pixabay and Pexels searches.
2. ANIMATION QUALITY: Use presets: "fade-up", "fade-in", "fade-down", "fade-out".
3. MOTION: Use "keyframes" to add subtle, professional motion (scale/opacity). E.g. scale 1.0 to 1.05.
4. QUALITY: No low-graded animation. Match the "feel and motive" of the script.
5. JSON: Return ONLY the JSON object. No conversational filler.
"""

        # Retry logic for individual scenes
        data = None
        for attempt in range(2):
            response = browser_ai.send_prompt(prompt, wait_time=5, timeout=90)
            data = extract_json(response) if response else None
            if data and "scout_scene" in data and "remotion_scene" in data:
                break
            print(f"   ⚠️ Attempt {attempt+1} failed for {scene_id}. Retrying...")
            time.sleep(2)

        if data and "scout_scene" in data and "remotion_scene" in data:
            final_scout_scenes.append(data["scout_scene"])
            final_remotion_scenes.append(data["remotion_scene"])
            print(f"   ✅ {scene_id} successful.")
        else:
            print(f"   ❌ {scene_id} failed after retries. Using safety fallback.")
            # Safety fallback to prevent breaking the final JSON structure
            fallback_duration_s = 7.0
            fallback_duration_f = 210
            final_scout_scenes.append({
                "scene_id": scene_id,
                "text": "cinematic atmosphere",
                "duration": fallback_duration_s,
                "audio_path": f"/content/drive/MyDrive/Counterism_Studio_V4/audio/SC_{str(i+1).zfill(2)}.wav",
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
                    "id": f"l{i+1}", "type": "text", "content": "...", "start": 15, "duration": fallback_duration_f - 30,
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

    with open(SCOUT_PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(scout_final, f, indent=2, ensure_ascii=False)
    print(f"✨ Updated {SCOUT_PLAN_PATH}")

    with open(REMOTION_PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(remotion_final, f, indent=2, ensure_ascii=False)
    print(f"✨ Updated {REMOTION_PLAN_PATH}")

    browser_ai.close()
    print("🎉 ALL SCENES PROCESSED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
