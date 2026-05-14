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
    """Translates Narrator blocks to ultra-modern Bangla using Gemini API."""
    print("🧠 [AI] Translating to ultra-modern Bangla via API...")

    pattern = r"(?im)^[\[\* ]*(Narrator|বর্ণনাকারী)[\:\*\] ]+\s*(.*?)(?=\s*\]?\n\s*(?:\[|\*\*|Narrator|বর্ণনাকারী|Scene|দৃশ্য|Music|সঙ্গীত|={5,})|\Z)"
    matches = list(re.finditer(pattern, script_content, re.DOTALL))

    if not matches:
        print("⚠️ No Narrator blocks found to translate.")
        return script_content

    print(f"✍️ [AI] Found {len(matches)} narrator blocks. Translating...")

    model = genai.GenerativeModel('gemini-2.0-flash')
    updated_script = script_content

    narrator_texts = [m.group(2).strip() for m in matches]
    combined_prompt = """You are a master documentary scriptwriter specializing in viral content.
    Translate the following segments into ultra-modern, "Gen-Z" trendy Bengali (Bangla).

    GUIDELINES:
    1. STYLE: Punchy and cinematic. NO formal "Sadhubhasha". Use the language of viral social media.
    2. VOCABULARY: Use fresh, trendy words. Keep common tech/cool English terms if they fit the vibe.
    3. HOOK: Every sentence must be a hook.
    4. MANDATORY: Return translations separated by '---SEG---'. No intro/outro.
    """
    for i, text in enumerate(narrator_texts):
        combined_prompt += f"\nSegment {i+1}:\n{text}\n"

    try:
        response = model.generate_content(combined_prompt)
        translated_segments = response.text.split("---SEG---")
        translated_segments = [s.strip() for s in translated_segments if s.strip()]

        for i in range(len(matches) - 1, -1, -1):
            match = matches[i]
            label = match.group(1)
            trans = translated_segments[i] if i < len(translated_segments) else match.group(2).strip()
            trans = re.sub(r"^(?i)Segment \d+:\s*", "", trans).strip()

            start_idx = match.start()
            end_idx = match.end()
            if end_idx < len(script_content) and script_content[end_idx] == ']': end_idx += 1

            original_full_block = script_content[start_idx:end_idx]
            if original_full_block.startswith("**"): replacement = f"**{label}:** {trans}"
            elif original_full_block.startswith("["): replacement = f"[{label}: {trans}]"
            else: replacement = f"{label}: {trans}"

            updated_script = updated_script[:start_idx] + replacement + updated_script[end_idx:]

    except Exception as e:
        print(f"❌ Translation failed: {e}")

    return updated_script

def split_scenes_browser(updated_script, language="en"):
    """Splits narrations into scenes with ONLY VO text using Browser Gemini."""
    print("🎬 [BROWSER] Generating high-end story VO segments...")

    browser_ai = BrowserAI(headless=True)
    browser_ai.start()

    pattern = r"(?im)^[\[\* ]*(Narrator|বর্ণনাকারী)[\:\*\] ]+\s*(.*?)(?=\s*\]?\n\s*(?:\[|\*\*|Narrator|বর্ণনাকারী|Scene|দৃশ্য|Music|সঙ্গীত|={5,})|\Z)"
    matches = list(re.finditer(pattern, updated_script, re.DOTALL))

    if not matches:
        browser_ai.close()
        return ""

    narrator_content = "\n\n".join([m.group(2).strip() for m in matches])
    is_bn = (language == "bn")
    scene_word = "দৃশ্য" if is_bn else "Scene"
    lang_label = "Bengali (Bangla)" if is_bn else "English"

    prompt = f"""You are a professional documentary editor. Divide the following Voice Over text into logical cinematic scenes in {lang_label}.

    REQUIREMENTS:
    1. THE OUTPUT MUST CONTAIN ONLY THE SPOKEN TEXT (VO) FOR EACH SCENE.
    2. NO VISUAL DESCRIPTIONS, NO CAMERA DIRECTIONS.
    3. FORMAT:
       {scene_word} 1
       The spoken text...

    4. NUMERALS: {"Bangla" if is_bn else "Standard"}.

    VO TEXT:
    {narrator_content}
    """

    story_content = ""
    try:
        story_content = browser_ai.send_prompt(prompt, wait_time=15)
        if not story_content: raise Exception("No response")
    except Exception as e:
        print(f"⚠️ Browser failed: {e}. Using API Fallback...")
        story_content = split_scenes_api_fallback(narrator_content, language)

    browser_ai.close()
    return story_content

def split_scenes_api_fallback(narrator_content, language="en"):
    print("🧠 [AI] Fallback scene generation...")
    model = genai.GenerativeModel('gemini-2.0-flash')
    is_bn = (language == "bn")
    scene_word = "দৃশ্য" if is_bn else "Scene"
    prompt = f"Divide this VO text into scenes. ONLY spoken text. No visuals. Format: {scene_word} 1\\nText\\n\\nText:\\n{narrator_content}"
    try:
        res = model.generate_content(prompt)
        return res.text
    except: return ""

def validate_content(content):
    topic_match = re.search(r"TOPIC:\s*(.*)", content)
    topic = topic_match.group(1).strip() if topic_match else ""
    script_match = re.search(r"(CINEMATIC SCRIPT.*?)\s*\n(.*?)(?:\n={10,}|$)", content, re.DOTALL | re.IGNORECASE)
    if not script_match:
        print("❌ Error: Heading missing.")
        sys.exit(1)
    script_content = script_match.group(2).strip()
    if not script_content:
        print("❌ Error: Script empty.")
        sys.exit(1)
    return topic, script_content, script_match

def main():
    print("🎬 SCENE SPLITER V4.5 - HYBRID HIGH-END")
    content = read_script()
    try:
        topic, script, match = validate_content(content)
        target_lang = "bn" if is_bangla(topic) else "en"

        updated_script = script
        if target_lang == "bn":
            updated_script = translate_narrator_blocks_api(script)

        # Save script_updated.txt
        start, end = match.span(2)
        new_content = content[:start] + updated_script + content[end:]
        with open(UPDATED_SCRIPT_FILE, "w", encoding="utf-8") as f: f.write(new_content)
        print(f"✅ Saved {UPDATED_SCRIPT_FILE}")

        # Generate story.txt
        story_content = split_scenes_browser(updated_script, language=target_lang)
        if story_content:
            with open(STORY_FILE, "w", encoding="utf-8") as f: f.write(story_content)
            print(f"✅ Saved {STORY_FILE}")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
