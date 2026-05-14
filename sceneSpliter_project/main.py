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

def read_script():
    if not os.path.exists(SCRIPT_FILE):
        print(f"❌ Error: {SCRIPT_FILE} not found.")
        sys.exit(1)

    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def is_bangla(text):
    """Detects if a string contains Bangla characters."""
    return bool(re.search(r'[\u0980-\u09ff]', text))

def translate_narrator_blocks_browser(script_content):
    """Translates Narrator blocks to Bangla using Browser-based Gemini for high quality."""
    print("🌐 [BROWSER] Initializing high-end translation engine...")

    # Flexible pattern for Narrator blocks:
    # Supports [Narrator: ...], **Narrator:** ..., Narrator: ...
    pattern = r"(?im)^[\[\* ]*(Narrator|বর্ণনাকারী)[\:\*\] ]+\s*(.*?)(?=\s*\]?\n\s*(?:\[|\*\*|Narrator|বর্ণনাকারী|Scene|দৃশ্য|Music|সঙ্গীত|={5,})|\Z)"

    matches = list(re.finditer(pattern, script_content, re.DOTALL))

    if not matches:
        print("⚠️ No Narrator blocks found to translate.")
        return script_content

    print(f"✍️ [BROWSER] Found {len(matches)} narrator blocks. Starting browser...")

    # Initialize browser
    browser_ai = BrowserAI(headless=True)
    browser_ai.start()

    updated_script = script_content

    narrator_texts = [m.group(2).strip() for m in matches]
    combined_prompt = """You are a master documentary scriptwriter and translator.
    Your task is to translate the following English narrator segments into high-end, extremely engaging, and hooky Bengali (Bangla).

    GUIDELINES:
    1. Use cinematic and professional language suitable for a top-tier YouTube documentary.
    2. The tone should be dramatic, evocative, and designed to keep viewers hooked.
    3. Ensure the flow is natural and carries emotional weight.
    4. MANDATORY: Return the translations as a list matching the order provided, separated by exactly '---SEG---'.
    5. DO NOT include any introductory text, segment numbers, or commentary. Just the translations.

    Segments to translate:
    """
    for i, text in enumerate(narrator_texts):
        combined_prompt += f"\nSegment {i+1}:\n{text}\n"

    try:
        response = browser_ai.send_prompt(combined_prompt, wait_time=10)
        if not response:
            raise Exception("No response from browser AI")

        translated_segments = response.split("---SEG---")
        translated_segments = [s.strip() for s in translated_segments if s.strip()]

        if len(translated_segments) != len(narrator_texts):
             print(f"⚠️ Segment count mismatch (Got {len(translated_segments)}, expected {len(narrator_texts)}). Cleaning response...")
             cleaned = []
             for s in translated_segments:
                 # Remove "Segment X:" or similar noise
                 s_clean = re.sub(r"^(?i)Segment \d+:\s*", "", s).strip()
                 if s_clean:
                     cleaned.append(s_clean)
             translated_segments = cleaned

        # Perform replacement in reverse order to preserve indices
        for i in range(len(matches) - 1, -1, -1):
            match = matches[i]
            label = match.group(1)

            # Find the full block to replace (including markers)
            start_idx = match.start()
            end_idx = match.end()
            # Check if there was a trailing bracket
            if end_idx < len(script_content) and script_content[end_idx] == ']':
                end_idx += 1

            trans = translated_segments[i] if i < len(translated_segments) else match.group(2).strip()

            # Reconstruct the block with its original markers
            original_full_block = script_content[start_idx:end_idx]

            # Find what the prefix was (e.g. "**Narrator:** " or "[Narrator: ")
            # We'll just use the match group 1 and some logic
            if original_full_block.startswith("**"):
                replacement = f"**{label}:** {trans}"
            elif original_full_block.startswith("["):
                replacement = f"[{label}: {trans}]"
            else:
                replacement = f"{label}: {trans}"

            updated_script = updated_script[:start_idx] + replacement + updated_script[end_idx:]

    except Exception as e:
        print(f"❌ High-end translation failed: {e}. Keeping original text.")

    browser_ai.close()
    return updated_script

def validate_content(content):
    # Extract TOPIC
    topic_match = re.search(r"TOPIC:\s*(.*)", content)
    topic = topic_match.group(1).strip() if topic_match else ""

    # Search for CINEMATIC SCRIPT heading
    script_pattern = r"(CINEMATIC SCRIPT.*?)\s*\n(.*?)(?:\n={10,}|$)"
    script_match = re.search(script_pattern, content, re.DOTALL | re.IGNORECASE)

    if not script_match:
        print("❌ Error: 'CINEMATIC SCRIPT' heading not found.")
        sys.exit(1)

    script_content = script_match.group(2).strip()

    if not script_content or script_content.isspace() or all(line.startswith("=") for line in script_content.splitlines()):
        print("❌ Error: 'CINEMATIC SCRIPT' section is empty.")
        sys.exit(1)

    return topic, script_content, script_match

def main():
    print("🎬 SCENE SPLITER ENGINE (V2.1) - HIGH-END BROWSER EDITION")
    print("==========================================================")

    content = read_script()
    print(f"✅ Successfully read {SCRIPT_FILE}")

    try:
        topic, script, match = validate_content(content)
        print(f"✅ Topic detected: {topic}")
        print("✅ Cinematic Script found and is not empty.")

        updated_script = script
        if is_bangla(topic):
            print("🌏 Bangla detected in topic. Translating Narrator blocks (High-End)...")
            updated_script = translate_narrator_blocks_browser(script)
            print("✅ Translation complete.")
        else:
            print("🌏 Topic is in English. Skipping translation.")

        # Re-construct the full file content
        start, end = match.span(2)
        new_content = content[:start] + updated_script + content[end:]

        with open(UPDATED_SCRIPT_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✨ SUCCESS! Updated script saved to: {UPDATED_SCRIPT_FILE}")

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
