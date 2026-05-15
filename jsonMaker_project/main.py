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

def main():
    print("🚀 [JSON_MAKER] Starting Engine...")

    script_content = read_file_content(SCRIPT_UPDATED)
    story_content = read_file_content(STORY_TXT)
    prep_content = read_file_content(JSON_PREP) or read_file_content(JSON_PREP_ALT)

    if not all([script_content, story_content, prep_content]):
        print(f"❌ Error: Missing input files in {AUDIO_DIR}")
        print(f"Script: {'OK' if script_content else 'MISSING'}")
        print(f"Story: {'OK' if story_content else 'MISSING'}")
        print(f"Prep: {'OK' if prep_content else 'MISSING'}")
        sys.exit(1)

    # Read existing JSON templates to respect format
    with open(SCOUT_PLAN_PATH, "r", encoding="utf-8") as f:
        scout_template = json.load(f)
    with open(REMOTION_PLAN_PATH, "r", encoding="utf-8") as f:
        remotion_template = json.load(f)

    # Detect language for fonts
    is_bn = bool(re.search(r'[\u0980-\u09ff]', story_content))
    target_lang = "Bengali (Bangla)" if is_bn else "English"

    # Initialize Browser AI
    browser_ai = BrowserAI(headless=True)
    browser_ai.start()

    prompt = f"""You are an expert video producer and JSON engineer. Your task is to populate two JSON files based on the provided cinematic script, story segments, and visual preparation guide.

IMPORTANT: The response MUST be a single, valid JSON object. Do not truncate the JSON. If there are many scenes, ensure every single one is included and all braces are closed correctly.

TARGET LANGUAGE: {target_lang}

INPUT DATA:
1. SCRIPT_UPDATED:
{script_content}

2. STORY_TXT (Narration per scene):
{story_content}

3. VISUAL_PREP (Suggested visuals and text layers):
{prep_content}

JSON SCHEMAS TO FILL:
--- SCOUT_PRODUCTION_PLAN_SCHEMA ---
{json.dumps(scout_template, indent=2)}

--- REMOTION_MASTER_JSON_SCHEMA ---
{json.dumps(remotion_template, indent=2)}

INSTRUCTIONS:
1. Parse the input into distinct scenes. Each "Scene X" or "দৃশ্য X" corresponds to one entry in the `scenes` array of BOTH JSON files.
2. For `production_plan.json` (Scout Project):
   - `text`: A concise description of the scene's visual content.
   - `duration`: Use seconds (float). Match the estimated duration of the narration.
   - `audio_duration`: Use seconds (float).
   - `scout_config.keywords`: Generate 2-3 high-quality keywords for searching on Pixabay/Pexels.
   - `scout_config.must_have_required`: Core subjects that MUST be in the footage.
3. For `master_remotion.json` (Remotion Project):
   - `duration`: Use frames (integer) at 30 FPS. Example: 5 seconds = 150 frames.
   - `background.src`: Use scene_X.mp4 (e.g., scene_1.mp4, scene_2.mp4).
   - `layers`: Each scene must have at least one 'text' layer using the 'Text Layer' suggestion from the VISUAL_PREP.
   - `style`: Position text layers appropriately (usually bottom-center like y: 1550).
   - `animationIn.type`: Use "fade-up" or "fade-in".
   - `animationOut.type`: Use "fade-down" or "fade-out".
   - `easing`: Use: "cubic-bezier(0.33, 1, 0.68, 1)", "ease-in", "ease-out", "ease-in-out", or "linear".
   - `transition.type`: Use "fade".
   - `textbox.type`: Use "rounded-rect", "rect", or "none".
   - `textAnimation.mode`: Use "word", "character", or "sentence".
   - CUSTOM MOTION: If a scene needs dynamic feel, add a `keyframes` array to the layer. Example: `[{{"frame": 0, "scale": 0.8, "opacity": 0}}, {{"frame": 30, "scale": 1, "opacity": 1}}]`.
4. COORDINATION: Ensure the scene IDs match across both files (scene_1, scene_2, etc.).
5. QUALITY: Animations must match the "feel and motive" of the script. No low-grade animations.
6. MANDATORY: Return ONLY a valid, MINIFIED JSON object (to save space) containing both results in this format:
{{
  "production_plan": {{ ... }},
  "master_remotion": {{ ... }}
}}
7. DO NOT include any conversational filler, introductory remarks, or markdown formatting (no ```json). Just the raw JSON.
"""

    print("💬 [JSON_MAKER] Sending data to Gemini...")
    # Increase timeout for potentially long generation
    response = browser_ai.send_prompt(prompt, wait_time=15, timeout=300)

    if not response:
        print("❌ Error: No response from Gemini.")
        browser_ai.close()
        sys.exit(1)

    # Robust JSON extraction
    json_str = response.strip()

    # Use regex to find the outermost JSON object
    match = re.search(r'(\{.*\})', json_str, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # Fallback to cleaning markdown
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            json_str = json_str.split("```")[1].strip()

    try:
        # Check for truncation
        if not json_str.endswith("}"):
            print("⚠️ [JSON_MAKER] JSON appears truncated. Attempting to fix...")
            # Simple heuristic: add closing braces if they are missing
            open_braces = json_str.count("{")
            close_braces = json_str.count("}")
            if open_braces > close_braces:
                json_str += "}" * (open_braces - close_braces)
                print(f"🔧 [JSON_MAKER] Added {open_braces - close_braces} closing braces.")

        data = json.loads(json_str)

        # Save production_plan.json
        with open(SCOUT_PLAN_PATH, "w", encoding="utf-8") as f:
            json.dump(data["production_plan"], f, indent=2, ensure_ascii=False)
        print(f"✅ Updated {SCOUT_PLAN_PATH}")

        # Save master_remotion.json
        # Merge some global properties if they were lost, though the AI should have kept them
        final_remotion = data["master_remotion"]
        final_remotion["width"] = remotion_template.get("width", 1080)
        final_remotion["height"] = remotion_template.get("height", 1920)
        final_remotion["fps"] = remotion_template.get("fps", 30)
        final_remotion["banglaFont"] = remotion_template.get("banglaFont", "FN Mahin Dui Dashok Italic")
        final_remotion["englishFont"] = remotion_template.get("englishFont", "Audiowide-Regular")

        with open(REMOTION_PLAN_PATH, "w", encoding="utf-8") as f:
            json.dump(final_remotion, f, indent=2, ensure_ascii=False)
        print(f"✅ Updated {REMOTION_PLAN_PATH}")

    except Exception as e:
        print(f"❌ Error parsing/saving JSON: {e}")
        print("Raw response snippet:", response[:500])

    browser_ai.close()
    print("🎉 Task complete.")

if __name__ == "__main__":
    main()
