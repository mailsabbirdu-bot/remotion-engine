import os
import sys
import re
import time
import google.generativeai as genai
from core.config import GEMINI_API_KEY
from core.browser_automator import BrowserAI

# Path discovery for Colab vs Local
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

AUDIO_DIR = os.path.join(BASE, "audio")
SCRIPT_FILE = os.path.join(AUDIO_DIR, "script.txt")
UPDATED_SCRIPT_FILE = os.path.join(AUDIO_DIR, "script_updated.txt")
STORY_FILE = os.path.join(AUDIO_DIR, "story.txt")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)

def read_script():
    if not os.path.exists(SCRIPT_FILE):
        print(f"❌ Error: {SCRIPT_FILE} not found.")
        sys.exit(1)

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def is_bangla(text):
    """Detects if a string contains Bangla characters."""
    return bool(re.search(r'[\u0980-\u09ff]', text))

def translate_narrator_blocks_api(script_content):
    """Translates Narrator blocks to ultra-modern Bangla using Gemini API with retries and fallback."""
    print("🧠 [AI] Translating to ultra-modern Bangla via API...")

    pattern = r"(?im)^[\[\* ]*(Narrator|বর্ণনাকারী)[\:\*\] ]+\s*(.*?)(?=\s*\]?\n\s*(?:\[|\*\*|Narrator|বর্ণনাকারী|Scene|দৃশ্য|Music|সঙ্গীত|={5,})|\Z)"
    matches = list(re.finditer(pattern, script_content, re.DOTALL))

    if not matches:
        print("⚠️ No Narrator blocks found to translate.")
        return script_content

    print(f"✍️ [AI] Found {len(matches)} narrator blocks. Translating...")

    # Models to try in order
    models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']
    updated_script = script_content

    narrator_texts = [m.group(2).strip() for m in matches]
    combined_prompt = """You are a master documentary scriptwriter specializing in viral content.
    Translate or rewrite the following narrator segments into ultra-modern, extremely hooky, and "Gen-Z/Millennial" trendy Bengali (Bangla).

    GUIDELINES:
    1. STYLE: Punchy, cinematic, and viral-ready. ABSOLUTELY NO formal "Sadhubhasha".
    2. VOCABULARY: Use fresh, trendy words that resonate with today's generation.
    3. HOOK: Every single sentence should feel like a hook.
    4. MANDATORY: Return the translations as a list matching the order provided, separated by exactly '---SEG---'.
    5. DO NOT include any introductory text, segment numbers, or commentary. Just the translations.

    Segments to translate:
    """
    for i, text in enumerate(narrator_texts):
        combined_prompt += f"\nSegment {i+1}:\n{text}\n"

    translated_segments = []
    success = False

    for model_name in models_to_try:
        if success: break
        print(f"🔄 Attempting translation with model: {model_name}...")
        try:
            model = genai.GenerativeModel(model_name)
            # Add exponential backoff retry for 429
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = model.generate_content(combined_prompt)
                    if response and response.text:
                        translated_segments = response.text.split("---SEG---")
                        translated_segments = [s.strip() for s in translated_segments if s.strip()]
                        if len(translated_segments) >= len(narrator_texts):
                            success = True
                            print(f"✅ Successfully translated using {model_name}")
                            break
                        else:
                            print(f"⚠️ Mismatch in segments (Got {len(translated_segments)}, expected {len(narrator_texts)}). Retrying...")
                except Exception as e:
                    if "429" in str(e):
                        wait = (2 ** attempt) * 5
                        print(f"⏳ Rate limited (429). Waiting {wait}s before retry...")
                        time.sleep(wait)
                    else:
                        raise e
            if success: break
        except Exception as e:
            print(f"❌ Failed with {model_name}: {e}")

    if not success:
        print("❌ All API translation attempts failed. Keeping original text.")
        return script_content

    # Clean up labels if AI added them
    cleaned_segments = []
    for s in translated_segments:
        s_clean = re.sub(r"^(?i)Segment \d+:\s*", "", s).strip()
        cleaned_segments.append(s_clean)

    # Perform replacement in reverse order
    for i in range(len(matches) - 1, -1, -1):
        match = matches[i]
        label = match.group(1)
        start_idx = match.start()
        end_idx = match.end()
        if end_idx < len(script_content) and script_content[end_idx] == ']':
            end_idx += 1

        trans = cleaned_segments[i] if i < len(cleaned_segments) else match.group(2).strip()

        original_full_block = script_content[start_idx:end_idx]
        if original_full_block.startswith("**"):
            replacement = f"**{label}:** {trans}"
        elif original_full_block.startswith("["):
            replacement = f"[{label}: {trans}]"
        else:
            replacement = f"{label}: {trans}"

        updated_script = updated_script[:start_idx] + replacement + updated_script[end_idx:]

    return updated_script

def split_scenes_browser(updated_script, language="en"):
    """Splits narrations into scenes with ONLY VO text using Browser-based Gemini."""
    print("🎬 [BROWSER] Generating high-end story VO segments...")

    # Extract only narrator parts
    pattern = r"(?im)^[\[\* ]*(Narrator|বর্ণনাকারী)[\:\*\] ]+\s*(.*?)(?=\s*\]?\n\s*(?:\[|\*\*|Narrator|বর্ণনাকারী|Scene|দৃশ্য|Music|সঙ্গীত|={5,})|\Z)"
    matches = list(re.finditer(pattern, updated_script, re.DOTALL))

    if not matches:
        print("⚠️ No narrator blocks found for scene analysis.")
        return ""

    narrator_content = "\n\n".join([f"{m.group(2).strip()}" for m in matches])
    is_bn = (language == "bn")
    scene_word = "দৃশ্য" if is_bn else "Scene"
    lang_label = "Bengali (Bangla)" if is_bn else "English"

    prompt = f"""You are a professional documentary editor and storyboard director.
    Take the following Voice Over (VO) text and divide it into logical, engaging cinematic scenes.

    VO TEXT CONTENT:
    {narrator_content}

    REQUIREMENTS:
    1. Break the text into several scenes. Each scene must contain a specific part of the spoken narration.
    2. THE OUTPUT MUST CONTAIN ONLY THE SPOKEN TEXT (Voice Over) FOR EACH SCENE.
    3. ABSOLUTELY NO camera directions, visual descriptions, or bracketed instructions. Just the lines to be spoken.
    4. LANGUAGE: The entire output MUST be in {lang_label}.
    5. FORMAT:
       {scene_word} 1
       [The spoken text for this scene]

       {scene_word} 2
       [The spoken text for this scene]

    6. NUMERALS: {"Use Bangla numerals (e.g., দৃশ্য ১, দৃশ্য ২)" if is_bn else "Use standard numerals (e.g., Scene 1, Scene 2)"}.
    7. Start directly with the first scene.
    """

    story_content = ""
    try:
        browser_ai = BrowserAI(headless=True)
        browser_ai.start()
        story_content = browser_ai.send_prompt(prompt, wait_time=15)
        browser_ai.close()
        if not story_content:
            raise Exception("No response from browser AI")
        print(f"✅ Story generation complete ({len(story_content)} chars).")
    except Exception as e:
        print(f"⚠️ Browser automation failed: {e}. Falling back to API...")
        story_content = split_scenes_api_fallback(narrator_content, language)

    return story_content.strip()

def split_scenes_api_fallback(narrator_content, language="en"):
    """Fallback story generator using API."""
    print("🧠 [AI] Falling back to API for story generation...")
    is_bn = (language == "bn")
    scene_word = "দৃশ্য" if is_bn else "Scene"
    lang_label = "Bengali (Bangla)" if is_bn else "English"

    prompt = f"""You are a professional documentary editor. Divide this Voice Over text into scenes in {lang_label}.
    Provide ONLY the spoken text for each scene. NO visual descriptions.
    FORMAT:
    {scene_word} 1
    [Spoken text]

    Text:
    {narrator_content}
    """
    # Try models in order
    models = ['gemini-2.0-flash', 'gemini-1.5-flash']
    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            res = model.generate_content(prompt)
            if res and res.text:
                return res.text
        except:
            continue
    return ""

def validate_content(content):
    topic_match = re.search(r"TOPIC:\s*(.*)", content)
    topic = topic_match.group(1).strip() if topic_match else ""

    script_match = re.search(r"(CINEMATIC SCRIPT.*?)\s*\n(.*?)(?:\n={10,}|$)", content, re.DOTALL | re.IGNORECASE)

    if not script_match:
        print("❌ Error: 'CINEMATIC SCRIPT' heading not found.")
        sys.exit(1)

    script_content = script_match.group(2).strip()
    if not script_content or script_content.isspace() or all(line.startswith("=") for line in script_content.splitlines()):
        print("❌ Error: 'CINEMATIC SCRIPT' section is empty.")
        sys.exit(1)

    return topic, script_content, script_match

def main():
    print("🎬 SCENE SPLITER ENGINE (V4.6) - HYBRID ROBUST")
    print("==============================================")

    content = read_script()
    print(f"✅ Successfully read {SCRIPT_FILE}")

    try:
        topic, script, match = validate_content(content)
        print(f"✅ Topic detected: {topic}")

        target_language = "bn" if is_bangla(topic) else "en"

        updated_script = script
        if target_language == "bn":
            updated_script = translate_narrator_blocks_api(script)
            print("✅ Translation process finished.")
        else:
            print("🌏 Topic is in English. Skipping translation.")

        # Re-construct the full file content
        start, end = match.span(2)
        new_content = content[:start] + updated_script + content[end:]

        with open(UPDATED_SCRIPT_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✨ Updated script saved to: {UPDATED_SCRIPT_FILE}")

        print("\n🔍 Generating story.txt (Divided Voice Overs)...")
        story_content = split_scenes_browser(updated_script, language=target_language)

        if story_content:
            with open(STORY_FILE, "w", encoding="utf-8") as f:
                f.write(story_content)
            print(f"✨ story.txt saved to: {STORY_FILE}")
        else:
            print("⚠️ Failed to generate story.txt")

        print("\n🎉 ALL TASKS COMPLETED SUCCESSFULLY!")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
