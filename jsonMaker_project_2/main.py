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
    scenes = [p.strip() for p in parts if p.strip()]

    # Fallback: if no scene markers found, treat the whole thing as one scene
    if not scenes and content.strip():
        print("⚠️ [DEBUG] No scene markers (Scene X / দৃশ্য X) found. Treating entire file as Scene 1.")
        return [content.strip()]
    return scenes

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
    print("\n" + "="*50)
    print("🚀 [ULTRA_DEBUG] JSON MAKER V2 ENGINE STARTING")
    print("="*50)

    # 1. Path Debugging
    print(f"📂 [DEBUG] DRIVE_BASE: {DRIVE_BASE}")
    print(f"📂 [DEBUG] LOCAL_BASE: {LOCAL_BASE}")
    print(f"📂 [DEBUG] SELECTED BASE: {BASE}")
    print(f"📂 [DEBUG] AUDIO_DIR: {AUDIO_DIR}")
    print(f"📂 [DEBUG] REPO_ROOT: {REPO_ROOT}")

    print(f"📄 [DEBUG] Target Scout Path: {SCOUT_PLAN_PATH}")
    print(f"📄 [DEBUG] Target Remotion Path: {REMOTION_PLAN_PATH}")
    print(f"📄 [DEBUG] Target Render Path: {MASTER_RENDER_PATH}")

    story_content = read_file_content(STORY_TXT)
    prep_content = read_file_content(JSON_PREP)

    print(f"🔍 [DEBUG] STORY_TXT exists: {os.path.exists(STORY_TXT)}")
    print(f"🔍 [DEBUG] JSON_PREP exists: {os.path.exists(JSON_PREP)}")

    if not story_content or not prep_content:
        print(f"❌ [CRITICAL] Error: Missing input files in {AUDIO_DIR}")
        print(f"   Check if story.txt and jsonPrep.txt exist in your Drive folder.")
        sys.exit(1)

    print(f"📖 [DEBUG] Story content length: {len(story_content)}")
    print(f"📖 [DEBUG] Prep content length: {len(prep_content)}")

    try:
        with open(SCOUT_PLAN_PATH, "r", encoding="utf-8") as f:
            scout_template = json.load(f)
            print(f"✅ [DEBUG] Loaded Scout template from {SCOUT_PLAN_PATH}")
    except Exception as e:
        print(f"⚠️ [DEBUG] Could not load Scout template: {e}. Using defaults.")
        scout_template = {"project_name": "Dynamic_Project", "scenes": []}

    try:
        with open(REMOTION_PLAN_PATH, "r", encoding="utf-8") as f:
            remotion_template = json.load(f)
            print(f"✅ [DEBUG] Loaded Remotion template from {REMOTION_PLAN_PATH}")
    except Exception as e:
        print(f"⚠️ [DEBUG] Could not load Remotion template: {e}. Using defaults.")
        remotion_template = {"width": 1080, "height": 1920, "fps": 30, "scenes": []}

    story_scenes = parse_scenes(story_content)
    prep_scenes = parse_scenes(prep_content)
    num_scenes = max(len(story_scenes), len(prep_scenes))

    print(f"📋 [DEBUG] Detected {len(story_scenes)} story scenes and {len(prep_scenes)} prep scenes.")
    print(f"📋 [DEBUG] Processing total of {num_scenes} scenes...")

    if num_scenes == 0:
        print("❌ [CRITICAL] No scenes detected to process. Exiting.")
        sys.exit(0)

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

        prompt = f"""Generate Production JSON for {batch_end - i} scenes.
STRICT MAPPING RULES:

1. Production Plan (Scout Engine):
   - scene_id: "scene_{idx}"
   - text: Comprehensive cinematic search prompt.
   - negative_prompts: ["low quality", "blurry", "text", "watermark", "people"]
   - audio_path: "/content/drive/MyDrive/Counterism_Studio_V4/audio/SC_{str(idx).zfill(2)}.wav"
   - scout_config:
     - keywords: MUST be descriptive phrases of 3-5 words (e.g., "blue whale swimming in deep ocean", "cinematic drone shot of dhaka city").
     - DO NOT provide single words like "blue", "whale", "dhaka". We need full phrases for accurate stock footage search.
     - must_have_required: The primary subject (e.g. ["blue whale"]).
   - audio_start_in_scene: 0.5
   - duration: "" (Exactly empty string)
   - audio_duration: "" (Exactly empty string)

2. Master Remotion / Render:
   - Id: "scene_{idx}"
   - duration: (AUDIO_DUR + 1.0) * 30 (rounded to integer frames)
   - src: "scene_{idx}.mp4"
   - background: {{"type": "video", "src": "scene_{idx}.mp4", "audio": ""}}
   - transition: {{"type": "fade", "duration": 15}}
   - Layers: [
       {{
         "id": "text_layer_{idx}",
         "type": "text",
         "content": "[Text from PREP]",
         "start": 0,
         "duration": [scene.duration],
         "style": {{ "color": "[Text Color from PREP]", "fontSize": 60 }},
         "animationIn": {{ "type": "fade-up", "easing": "cubic-bezier(0.33, 1, 0.68, 1)" }},
         "animationOut": {{ "type": "fade-out", "easing": "cubic-bezier(0.33, 1, 0.68, 1)" }},
         "textAnimation": {{ "mode": "word", "duration": 40 }},
         "textbox": {{
            "enabled": [true/false],
            "type": "[rect/rounded-rect/none]",
            "color": "[Textbox Color from PREP]"
         }}
       }}
     ]

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
        print(f"🤖 [DEBUG] AI Response received ({len(response) if response else 0} chars)")

        data = extract_json(response)

        if data and "scenes" in data:
            print(f"✅ [DEBUG] Successfully extracted {len(data['scenes'])} scenes from AI response.")
            for scene_data in data["scenes"]:
                final_scout_scenes.append(scene_data["scout"])

                # Clean up Remotion scene keys
                rem = scene_data["remotion"]
                # Ensure we only use 'Id' and 'Layers' (capitalized) as requested
                # Use pop to move the value to the new key and remove the old one
                if "id" in rem: rem["Id"] = rem.pop("id")
                if "layers" in rem: rem["Layers"] = rem.pop("layers")

                # Double check no lowercase duplicates exist
                rem.pop("id", None)
                rem.pop("layers", None)

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

    # The React components handle both casing, but we'll export strictly as 'Layers' and 'Id'
    # for the JSON files to match user preference.

    print(f"💾 [DEBUG] Writing Scout Plan to: {SCOUT_PLAN_PATH}")
    with open(SCOUT_PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(scout_final, f, indent=2, ensure_ascii=False)
    print(f"✔️ [DEBUG] Scout File Written. Size: {os.path.getsize(SCOUT_PLAN_PATH)} bytes")

    print(f"💾 [DEBUG] Writing Remotion Plan to: {REMOTION_PLAN_PATH}")
    with open(REMOTION_PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(remotion_final, f, indent=2, ensure_ascii=False)
    print(f"✔️ [DEBUG] Remotion File Written. Size: {os.path.getsize(REMOTION_PLAN_PATH)} bytes")

    print(f"💾 [DEBUG] Writing Master Render to: {MASTER_RENDER_PATH}")
    with open(MASTER_RENDER_PATH, "w", encoding="utf-8") as f:
        json.dump(remotion_final, f, indent=2, ensure_ascii=False)
    print(f"✔️ [DEBUG] Render File Written. Size: {os.path.getsize(MASTER_RENDER_PATH)} bytes")

    # 5. DRIVE SYNC (Crucial for user visibility in Colab)
    print(f"🔄 [DEBUG] Syncing to Drive/Local Base: {BASE}")
    DRIVE_SCOUT = os.path.join(BASE, "manifests", "production_plan.json")
    DRIVE_REMOTION = os.path.join(BASE, "master_remotion.json")
    DRIVE_RENDER = os.path.join(BASE, "master_render.json")

    try:
        os.makedirs(os.path.dirname(DRIVE_SCOUT), exist_ok=True)

        with open(DRIVE_SCOUT, "w", encoding="utf-8") as f:
            json.dump(scout_final, f, indent=2, ensure_ascii=False)
        print(f"📡 [DEBUG] Sync'd Scout to Drive: {DRIVE_SCOUT}")

        with open(DRIVE_REMOTION, "w", encoding="utf-8") as f:
            json.dump(remotion_final, f, indent=2, ensure_ascii=False)
        print(f"📡 [DEBUG] Sync'd Remotion to Drive: {DRIVE_REMOTION}")

        with open(DRIVE_RENDER, "w", encoding="utf-8") as f:
            json.dump(remotion_final, f, indent=2, ensure_ascii=False)
        print(f"📡 [DEBUG] Sync'd Render to Drive: {DRIVE_RENDER}")

    except Exception as e:
        print(f"⚠️ [DEBUG] Drive Sync failed: {e}")

    print(f"✅ [ULTRA_DEBUG] ALL ACTIONS COMPLETED SUCCESSFULLY.")
    browser_ai.close()

if __name__ == "__main__":
    main()
