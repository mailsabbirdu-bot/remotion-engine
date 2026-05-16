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
VOICEOVER_FILE = os.path.join(AUDIO_DIR, "voiceOver.txt")
JSONPREP_FILE = os.path.join(AUDIO_DIR, "jsonPrep.txt")

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

    # Ultra-flexible pattern for Narrator blocks
    pattern = r"(?:\*\*|\[)?\s*(Narrator|বর্ণনাকারী)\s*[\:\*\] ]+\s*(.*?)(?=\s*(?:\*\*|\[|Narrator|বর্ণনাকারী|Scene|দৃশ্য|Music|সঙ্গীত|={5,})|\Z)"
    matches = list(re.finditer(pattern, script_content, re.DOTALL | re.IGNORECASE))

    if not matches:
        print("⚠️ No Narrator blocks found to translate. Regex might need adjustment.")
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

            start_idx = match.start()
            end_idx = match.end()

            trans = translated_segments[i] if i < len(translated_segments) else match.group(2).strip()
            # Clean up AI noise
            trans = re.sub(r"^Segment \d+:\s*", "", trans, flags=re.IGNORECASE).strip()

            # Reconstruct with original header formatting
            original_full_block_head = script_content[start_idx:match.start(2)]

            replacement = f"{original_full_block_head}{trans}"
            updated_script = updated_script[:start_idx] + replacement + updated_script[end_idx:]

        print("✅ Translation complete.")
    except Exception as e:
        print(f"❌ Translation failed: {e}. Keeping original text.")

    return updated_script

def split_scenes_browser(browser_ai, updated_script, language="en"):
    """Splits narrations into short 6-8s scenes based on footage blocks using Browser Gemini."""
    print("\n🎬 [BROWSER] Dividing narrations into ultra-short cinematic scenes (6-8s focus)...")

    is_bn = (language == "bn")
    lang_label = "Bengali (Bangla)" if is_bn else "English"
    scene_word = "দৃশ্য" if is_bn else "Scene"

    prompt = f"""You are a professional documentary film editor specializing in fast-paced, viral social media content.
    I will provide you with a cinematic script that contains [Visual: ...] blocks and Narrator text.

    YOUR GOAL:
    Divide the narration into logical, short scenes where NO SINGLE SCENE lasts longer than 6 to 8 seconds on screen.

    RULES:
    1. A scene typically averages 15-20 words to fit the 6-8 second window. If a block of narration is longer, you MUST break it into multiple scenes (Scene 1, Scene 2, etc.) even if the visual description doesn't change.
    2. Synchronize the scene breaks with the [Visual: ...] blocks provided in the script.
    3. THE OUTPUT MUST CONTAIN ONLY THE SPOKEN TEXT (VO) FOR EACH SCENE.
    4. ABSOLUTELY NO camera directions, visual descriptions, or bracketed instructions in the final output.
    5. LANGUAGE: The entire output MUST be in {lang_label}.
    6. FORMAT:
       {scene_word} 1
       [The spoken text for this scene]

       {scene_word} 2
       [The spoken text for this scene]

    7. NUMERALS: {"Use Bangla numerals (e.g., দৃশ্য ১, দৃশ্য ২)" if is_bn else "Use standard numerals (e.g., Scene 1, Scene 2)"}.
    8. Start directly with the first scene.

    CINEMATIC SCRIPT:
    {updated_script}
    """

    story_content = ""
    try:
        story_content = browser_ai.send_prompt(prompt, wait_time=20)
        if not story_content:
            raise Exception("No response from browser AI for story generation")

        print(f"✅ Story generation complete ({len(story_content)} chars).")
    except Exception as e:
        print(f"❌ Story generation failed: {e}")

    return story_content.strip()

def generate_json_prep(browser_ai, story_content, language="en"):
    """Generates advanced visual preparation guide (jsonPrep) with specific fields."""
    print("\n🎬 [BROWSER] Generating advanced visual preparation guide (jsonPrep)...")

    is_bn = (language == "bn")
    scene_word = "দৃশ্য" if is_bn else "Scene"
    text_lang = "Bengali (Bangla)" if is_bn else "English"

    prompt = f"""You are a professional visual director and motion graphics designer for a top-tier YouTube channel.
    Analyze the following storyboard (Scene-by-scene Voice Over) and provide detailed visual and motion design instructions for every scene.

    STORYBOARD CONTENT:
    {story_content}

    PRESET OPTIONS (Use ONLY these values where applicable):
    - Textbox Shapes: 'rounded-rect', 'rect', 'none'
    - Animations (In): 'fade-up', 'fade-in'
    - Animations (Out): 'fade-down', 'fade-out'
    - Transitions: 'fade'
    - Easing: 'cubic-bezier(0.33, 1, 0.68, 1)', 'ease-in-out', 'ease-in', 'ease-out', 'linear'

    REQUIREMENTS FOR EACH SCENE:
    1. scout: Suggest specific, cinematic stock footage keywords (for Pixabay/Pexels) in English.
    2. Text: Short, hooky text layer content. Use {text_lang}.
    3. Textbox: Shape of the textbox (choose from presets).
    4. Animation: Animation for the text and textbox (In and Out from presets).
    5. Color: Suggest a Hex color for text and a complementary RGBA color for the textbox (e.g., #ffffff, rgba(0,0,0,0.6)).
    6. Transition: Transition from this scene to the next (choose from presets).

    FORMAT (Strictly follow this style):
    {scene_word} 1
    scout: [Keywords in English]
    Text: [Content in {text_lang}]
    Textbox: [Shape preset]
    Animation: [In preset] / [Out preset] / [Easing preset]
    Color: [Text Hex] / [Textbox RGBA]
    Transition: [Transition preset]

    {scene_word} 2
    scout: [Keywords in English]
    Text: [Content in {text_lang}]
    Textbox: [Shape preset]
    Animation: [In preset] / [Out preset] / [Easing preset]
    Color: [Text Hex] / [Textbox RGBA]
    Transition: [Transition preset]

    Start directly with the first scene.
    """

    prep_content = ""
    try:
        prep_content = browser_ai.send_prompt(prompt, wait_time=20)
        if not prep_content:
            raise Exception("No response from browser AI for visual prep")

        print(f"✅ Visual prep complete ({len(prep_content)} chars).")
    except Exception as e:
        print(f"❌ Visual prep generation failed: {e}")

    return prep_content.strip()

def generate_voiceover_text(story_content):
    """Strips scene headers to create a pure VO text file."""
    # Pattern to match "Scene X" or "दृश्य X" at the start of a line
    pattern = r"^(?:Scene|দৃশ্য)\s*[\d০-৯]+\s*$"
    lines = story_content.splitlines()
    vo_lines = [line for line in lines if not re.match(pattern, line.strip(), re.IGNORECASE)]
    return "\n".join(vo_lines).strip()

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
    print("🎬 SCENE SPLITER ENGINE (V6.1) - FAST-PACED SOCIAL MEDIA EDITION")
    print("================================================================")

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

        # 2. Generate story.txt using the full updated script for context
        story_content = split_scenes_browser(browser_ai, updated_script, language=target_language)

        if story_content:
            with open(STORY_FILE, "w", encoding="utf-8") as f:
                f.write(story_content)
            print(f"✨ story.txt saved to: {STORY_FILE}")

            # 3. Generate voiceOver.txt
            vo_text = generate_voiceover_text(story_content)
            with open(VOICEOVER_FILE, "w", encoding="utf-8") as f:
                f.write(vo_text)
            print(f"✨ voiceOver.txt saved to: {VOICEOVER_FILE}")

            # 4. Generate jsonPrep.txt
            prep_content = generate_json_prep(browser_ai, story_content, language=target_language)
            if prep_content:
                with open(JSONPREP_FILE, "w", encoding="utf-8") as f:
                    f.write(prep_content)
                print(f"✨ jsonPrep.txt saved to: {JSONPREP_FILE}")
        else:
            print("⚠️ Failed to generate story.txt, skipping VO and Prep.")

        browser_ai.close()
        print("\n🎉 ALL TASKS COMPLETED SUCCESSFULLY!")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
