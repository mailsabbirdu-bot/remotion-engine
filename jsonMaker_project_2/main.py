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

# Source files
STORY_TXT = os.path.join(AUDIO_DIR, "story.txt")
JSON_PREP = os.path.join(AUDIO_DIR, "jsonPrep.txt")

# Target files in Repository
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)

SCOUT_PLAN_PATH = os.path.join(REPO_ROOT, "scout_project", "manifests", "production_plan.json")
REMOTION_PLAN_PATH = os.path.join(REPO_ROOT, "remotion_project", "src", "master_remotion.json")
MASTER_RENDER_PATH = os.path.join(REPO_ROOT, "remotion_project", "src", "master_render.json")

def read_file_content(filepath):
    if not os.path.exists(filepath):
        return None
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def get_audio_duration(scene_idx):
    """Calculates audio duration using wave or fallback."""
    audio_path = os.path.join(AUDIO_DIR, f"SC_{str(scene_idx).zfill(2)}.wav")

    if os.path.exists(audio_path):
        try:
            with wave.open(audio_path, 'rb') as f:
                frames = f.getnframes()
                rate = f.getframerate()
                return frames / float(rate)
        except:
            pass

    return 8.0 # Default fallback

def parse_scenes(content):
    """Splits content into scenes."""
    if not content: return []
    pattern = r'(?m)^(?:Scene|দৃশ্য)\s*(?:[০-৯\d]+)'
    parts = re.split(pattern, content)
    return [p.strip() for p in parts if p.strip()]

def extract_json(response):
    """Extracts a JSON object from AI response strings with extreme robustness."""
    if not response: return None

    # Pre-cleaning: Remove potential non-JSON preamble/epilogue
    match = re.search(r'([\[\{].*[\]\}])', response, re.DOTALL)
    if not match:
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
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
    json_str = re.sub(r'\}\s*\{', '}, {', json_str)
    json_str = re.sub(r'\]\s*\[', '], [', json_str)
    json_str = re.sub(r'\]\s*\{', '], {', json_str)
    json_str = json_str.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")

    def balance_json(s):
        braces = s.count('{') - s.count('}')
        brackets = s.count('[') - s.count(']')
        if brackets > 0: s += ']' * brackets
        if braces > 0: s += '}' * braces
        return s

    try:
        return json.loads(json_str)
    except:
        try:
            return json.loads(balance_json(json_str))
        except:
            return None

def main():
    print("🚀 [JSON_MAKER_V2] Starting Engine...")

    story_content = read_file_content(STORY_TXT)
    prep_content = read_file_content(JSON_PREP)

    if not story_content or not prep_content:
        print(f"❌ Error: Missing input files in {AUDIO_DIR}")
        sys.exit(1)

    try:
        with open(SCOUT_PLAN_PATH, "r", encoding="utf-8") as f:
            scout_template = json.load(f)
    except:
        scout_template = {"project_name": "Dynamic_Project", "scenes": []}

    try:
        with open(REMOTION_PLAN_PATH, "r", encoding="utf-8") as f:
            remotion_template = json.load(f)
    except:
        remotion_template = {"width": 1080, "height": 1920, "fps": 30, "scenes": []}

    story_scenes = parse_scenes(story_content)
    prep_scenes = parse_scenes(prep_content)
    num_scenes = max(len(story_scenes), len(prep_scenes))

    print(f"📋 Processing {num_scenes} scenes...")

    browser_ai = BrowserAI(headless=True)
    browser_ai.start()

    final_scout_scenes = []
    final_remotion_scenes = []

    batch_size = 4
    for i in range(0, num_scenes, batch_size):
        batch_end = min(i + batch_size, num_scenes)
        print(f"🎬 Batch {i+1}-{batch_end}...")

        batch_input = ""
        for j in range(batch_end - i):
            idx = i + j + 1
            s = story_scenes[i + j] if (i + j) < len(story_scenes) else ""
            p = prep_scenes[i + j] if (i + j) < len(prep_scenes) else ""
            dur = get_audio_duration(idx)
            batch_input += f"### SCENE {idx} ###\nAUDIO_DUR: {dur:.2f}\nSTORY: {s}\nPREP: {p}\n\n"

        prompt = f"""Generate JSON for {batch_end - i} scenes.
Follow these mapping rules strictly:

For each scene:
1. Production Plan (Scout):
   - scene_id: "scene_{{idx}}"
   - text: Extract cinematic search description from PREP 'scout' field.
   - negative_prompts: ["low quality", "blurry", "text", "watermark", "people"] + any specific negatives from PREP.
   - asset_preferences: {{"allow_video": true, "allow_image": true, "preferred_type": "video"}}.
   - audio_path: "/content/drive/MyDrive/Counterism_Studio_V4/audio/SC_{{idx_padded}}.wav" (e.g. SC_01.wav for scene 1).
   - scout_config: Extract keywords, must_have_required, must_have_optional from PREP 'scout' and 'keywords'.
   - audio_start_in_scene: 0.5
   - duration: "" (EMPTY STRING)
   - audio_duration: "" (EMPTY STRING)

2. Master Remotion:
   - Id: "scene_{{idx}}"
   - duration: (AUDIO_DUR + 1.0) * 30 (as integer frames)
   - src: "scene_{{idx}}.mp4"
   - background: {{"type": "video", "src": "scene_{{idx}}.mp4", "audio": ""}}
   - transition: Extract type (e.g. fade) and duration (e.g. 15) from PREP.
   - Layers: [] (Fill this array with layer objects).
   - Each Layer object must have: id, type, content, start, duration, style, animationIn, animationOut, textAnimation, textbox.
     - content: Use 'Text' from PREP.
     - textbox: Use 'Textbox' from PREP. If 'none', enabled: false.
     - animation: Use 'Animation' (In / Out / Easing) from PREP.
     - color: Use 'Color' (Text / Textbox) from PREP.

OUTPUT FORMAT:
{{
  "scenes": [
    {{
      "scout": {{ ... }},
      "remotion": {{ ... }}
    }}
  ]
}}

INPUT DATA:
{batch_input}
"""
        response = browser_ai.send_prompt(prompt)
        data = extract_json(response)

        if data and "scenes" in data:
            for scene_data in data["scenes"]:
                final_scout_scenes.append(scene_data["scout"])

                # Fix casing for Remotion if AI didn't follow prompt perfectly
                rem = scene_data["remotion"]
                if "Id" not in rem and "id" in rem: rem["Id"] = rem.pop("id")
                if "Layers" not in rem and "layers" in rem: rem["Layers"] = rem.pop("layers")

                final_remotion_scenes.append(rem)
        else:
            print(f"⚠️ Batch failed, using fallback...")
            # Fallback logic omitted for brevity in this step, but good practice to include
            for k in range(i, batch_end):
                idx = k + 1
                final_scout_scenes.append({
                    "scene_id": f"scene_{idx}", "text": "cinematic background", "duration": "", "audio_duration": "",
                    "audio_path": f"/content/drive/MyDrive/Counterism_Studio_V4/audio/SC_{str(idx).zfill(2)}.wav",
                    "audio_start_in_scene": 0.5, "negative_prompts": ["low quality"],
                    "asset_preferences": {"allow_video": True, "allow_image": True, "preferred_type": "video"},
                    "scout_config": {"keywords": ["cinematic"], "must_have_required": [], "must_have_optional": []}
                })
                final_remotion_scenes.append({
                    "Id": f"scene_{idx}", "duration": 240,
                    "src": f"scene_{idx}.mp4",
                    "background": {"type": "video", "src": f"scene_{idx}.mp4", "audio": ""},
                    "transition": {"type": "fade", "duration": 15},
                    "Layers": []
                })

    scout_final = scout_template.copy()
    scout_final["scenes"] = final_scout_scenes

    remotion_final = remotion_template.copy()
    remotion_final["scenes"] = final_remotion_scenes

    # User requested capitalized 'Layers' but backup shows 'layers'.
    # We provide both to be safe or map it correctly if engine produced lowercase
    for scene in remotion_final["scenes"]:
        if "Layers" in scene:
            scene["layers"] = scene["Layers"]

    with open(SCOUT_PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(scout_final, f, indent=2, ensure_ascii=False)

    with open(REMOTION_PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(remotion_final, f, indent=2, ensure_ascii=False)

    with open(MASTER_RENDER_PATH, "w", encoding="utf-8") as f:
        json.dump(remotion_final, f, indent=2, ensure_ascii=False)

    print(f"✅ Successfully updated JSON files.")
    browser_ai.close()

if __name__ == "__main__":
    main()
