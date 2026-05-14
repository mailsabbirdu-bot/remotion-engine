import os
import sys
import re
import time
from core.browser_automator import BrowserAI

# Path discovery for Colab vs Local
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

AUDIO_DIR = os.path.join(BASE, "audio")
SCRIPT_FILE = os.path.join(AUDIO_DIR, "script.txt")
UPDATED_SCRIPT_FILE = os.path.join(AUDIO_DIR, "script_updated.txt")
STORY_FILE = os.path.join(AUDIO_DIR, "story.txt")

def read_script():
    if not os.path.exists(SCRIPT_FILE):
        print(f"❌ Error: {SCRIPT_FILE} not found.")
        sys.exit(1)

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def is_bangla(text):
    """Detects if a string contains Bangla characters."""
    return bool(re.search(r'[\u0980-\u09ff]', text))

def translate_narrator_blocks_browser(browser_ai, script_content):
    """Translates Narrator blocks to ultra-modern Bangla using Browser-based Gemini."""
    print("✍️ [BROWSER] Translating Narrator blocks to ultra-modern Bangla...")

    # Flexible pattern for Narrator blocks
    pattern = r"(?im)^[\[\* ]*(Narrator|বর্ণনাকারী)[\:\*\] ]+\s*(.*?)(?=\s*\]?\n\s*(?:\[|\*\*|Narrator|বর্ণনাকারী|Scene|দৃশ্য|Music|সঙ্গীত|={5,})|\Z)"
    matches = list(re.finditer(pattern, script_content, re.DOTALL))

    if not matches:
        print("⚠️ No Narrator blocks found to translate.")
        return script_content

    print(f"✍️ [BROWSER] Found {len(matches)} narrator blocks. Processing...")

    narrator_texts = [m.group(2).strip() for m in matches]
    combined_prompt = """You are a master documentary scriptwriter and translator specializing in viral social media content.
    Your task is to translate or rewrite the following narrator segments into ultra-modern, extremely hooky, and "Gen-Z/Millennial" trendy Bengali (Bangla).

    GUIDELINES:
    1. STYLE: Ultra-modern, punchy, and cinematic. ABSOLUTELY AVOID "textbook" or formal "Sadhubhasha". No "Kothito" or "Suddho" formal words that sound like a news broadcast. Use the language of the internet, the youth, and viral YouTube storytellers.
    2. VOCABULARY: Use trendy, fresh, and powerful Bengali words. If a modern English term is commonly used by the generation (like 'Hub', 'Startup', 'Tech', 'Vibe'), feel free to keep it or use the Bengali phonetic version if it sounds cooler.
    3. HOOK: Every single sentence must be a "hook". It should create a "WOW" factor. The narration should be addictive.
    4. TONE: High-energy, professional yet "cool" and "edgy". Think of high-end Netflix tech-documentaries or viral international storytellers.
    5. FLOW: Short, rhythmic, and emotionally charged sentences.
    6. MANDATORY: Return the translations as a list matching the order provided, separated by exactly '---SEG---'.
    7. DO NOT include any introductory text, segment numbers, or commentary. Just the translations.

    Segments to translate:
    """
    for i, text in enumerate(narrator_texts):
        combined_prompt += f"\nSegment {i+1}:\n{text}\n"

    updated_script = script_content
    try:
        response = browser_ai.send_prompt(combined_prompt, wait_time=15)
        if not response:
            raise Exception("No response from Browser AI")

        translated_segments = response.split("---SEG---")
        translated_segments = [s.strip() for s in translated_segments if s.strip()]

        if len(translated_segments) < len(narrator_texts):
             print(f"⚠️ Segment count mismatch (Got {len(translated_segments)}, expected {len(narrator_texts)}).")

        # Perform replacement in reverse order to preserve indices
        for i in range(len(matches) - 1, -1, -1):
            match = matches[i]
            label = match.group(1)

            start_idx = match.start()
            end_idx = match.end()
            if end_idx < len(script_content) and script_content[end_idx] == ']':
                end_idx += 1

            trans = translated_segments[i] if i < len(translated_segments) else match.group(2).strip()
            trans = re.sub(r"^(?i)Segment \d+:\s*", "", trans).strip()

            original_full_block = script_content[start_idx:end_idx]
            if original_full_block.startswith("**"):
                replacement = f"**{label}:** {trans}"
            elif original_full_block.startswith("["):
                replacement = f"[{label}: {trans}]"
            else:
                replacement = f"{label}: {trans}"

            updated_script = updated_script[:start_idx] + replacement + updated_script[end_idx:]

        print("✅ Translation complete.")
    except Exception as e:
        print(f"❌ Translation failed: {e}. Keeping original text.")

    return updated_script

def split_scenes_browser(browser_ai, updated_script, language="en"):
    """Splits narrations into scenes with ONLY VO text using Browser-based Gemini."""
    print("\n🎬 [BROWSER] Dividing narrations into scenes (Voice Over text focus)...")

    # Extract only narrator parts
    pattern = r"(?im)^[\[\* ]*(Narrator|বর্ণনাকারী)[\:\*\] ]+\s*(.*?)(?=\s*\]?\n\s*(?:\[|\*\*|Narrator|বর্ণনাকারী|Scene|দৃশ্য|Music|সঙ্গীত|={5,})|\Z)"
    matches = list(re.finditer(pattern, updated_script, re.DOTALL))

    if not matches:
        print("⚠️ No narrator blocks found for scene analysis.")
        return ""

    narrator_content = "\n\n".join([f"{m.group(2).strip()}" for m in matches])

    is_bn = (language == "bn")
    lang_label = "Bengali (Bangla)" if is_bn else "English"
    scene_word = "দৃশ্য" if is_bn else "Scene"

    prompt = f"""You are a professional documentary editor.
    Take the following Voice Over (VO) text and divide it into logical, engaging cinematic scenes in {lang_label}.

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
        story_content = browser_ai.send_prompt(prompt, wait_time=15)
        if not story_content:
            raise Exception("No response from browser AI for story generation")

        print(f"✅ Story generation complete ({len(story_content)} chars).")
    except Exception as e:
        print(f"❌ Story generation failed: {e}")

    return story_content.strip()

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
    print("🎬 SCENE SPLITER ENGINE (V5.0) - FULL BROWSER AUTOMATION")
    print("==========================================================")

    content = read_script()
    print(f"✅ Successfully read {SCRIPT_FILE}")

    try:
        topic, script, match = validate_content(content)
        print(f"✅ Topic detected: {topic}")

        target_language = "bn" if is_bangla(topic) else "en"

        # Initialize Browser AI once
        browser_ai = BrowserAI(headless=True)
        print("🌐 [BROWSER] Initializing engine...")
        browser_ai.start()

        updated_script = script
        if target_language == "bn":
            print("🌏 Bangla detected in topic. Starting translation...")
            updated_script = translate_narrator_blocks_browser(browser_ai, script)
        else:
            print("🌏 Topic is in English. Skipping translation.")

        # Re-construct the full file content
        start, end = match.span(2)
        new_content = content[:start] + updated_script + content[end:]

        with open(UPDATED_SCRIPT_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✨ Updated script saved to: {UPDATED_SCRIPT_FILE}")

        # Generate story.txt
        story_content = split_scenes_browser(browser_ai, updated_script, language=target_language)

        if story_content:
            with open(STORY_FILE, "w", encoding="utf-8") as f:
                f.write(story_content)
            print(f"✨ story.txt saved to: {STORY_FILE}")
        else:
            print("⚠️ Failed to generate story.txt")

        browser_ai.close()
        print("\n🎉 ALL TASKS COMPLETED SUCCESSFULLY!")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
