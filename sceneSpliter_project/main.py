import os
import sys
import re
import google.generativeai as genai
from core.config import GEMINI_API_KEY

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

def translate_narrator_blocks(script_content):
    """Translates Narrator blocks to Bangla using Gemini."""
    genai.configure(api_key=GEMINI_API_KEY)

    # Using a model that exists in this environment
    model = genai.GenerativeModel('gemini-2.0-flash')

    def translate_match(match):
        label = match.group(1) # Narrator or বর্ণনাকারী
        text = match.group(2)

        prompt = f"Translate the following documentary narration text into pure Bengali (Bangla). Provide only the translated text, no extra commentary:\n\n{text}"

        try:
            response = model.generate_content(prompt)
            translated_text = response.text.strip()
            return f"[{label}: {translated_text}]"
        except Exception as e:
            print(f"⚠️ Translation failed for block: {text[:50]}... Error: {e}")
            return match.group(0)

    # Pattern to match [Narrator: text] or [বর্ণনাকারী: text]
    pattern = r"\[(Narrator|বর্ণনাকারী):\s*(.*?)\]"
    updated_script = re.sub(pattern, translate_match, script_content, flags=re.DOTALL)

    return updated_script

def validate_content(content):
    # Extract TOPIC
    topic_match = re.search(r"TOPIC:\s*(.*)", content)
    topic = topic_match.group(1).strip() if topic_match else ""

    # Search for CINEMATIC SCRIPT heading
    # It looks for the heading and captures everything after it until the next separator
    script_pattern = r"(CINEMATIC SCRIPT.*?)\s*\n(.*?)(?:\n={10,}|$)"
    script_match = re.search(script_pattern, content, re.DOTALL | re.IGNORECASE)

    if not script_match:
        print("❌ Error: 'CINEMATIC SCRIPT' heading not found.")
        sys.exit(1)

    script_content = script_match.group(2).strip()

    # Check if the content is empty or just contains separators
    if not script_content or script_content.isspace() or all(line.startswith("=") for line in script_content.splitlines()):
        print("❌ Error: 'CINEMATIC SCRIPT' section is empty.")
        sys.exit(1)

    return topic, script_content, script_match

def main():
    print("🎬 SCENE SPLITER ENGINE (V1.2)")
    print("==============================")

    content = read_script()
    print(f"✅ Successfully read {SCRIPT_FILE}")

    try:
        topic, script, match = validate_content(content)
        print(f"✅ Topic detected: {topic}")
        print("✅ Cinematic Script found and is not empty.")

        updated_script = script
        if is_bangla(topic):
            print("🌏 Bangla detected in topic. Translating Narrator blocks...")
            updated_script = translate_narrator_blocks(script)
            print("✅ Translation complete.")
        else:
            print("🌏 Topic is in English. Skipping translation.")

        # Re-construct the full file content
        # Group 2 of the match is the script content
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
