import os
import sys
import re
import shutil

from core.pipeline import ResearchPipeline

# Path discovery for Colab vs Local
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

OUTPUT_DIR = os.path.join(BASE, "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def is_bangla(text):
    """Detects if a string contains Bangla characters."""
    return bool(re.search(r'[\u0980-\u09ff]', text))

def main():
    # Ensure we are in the project directory
    if not os.path.exists("core/pipeline.py"):
        print("❌ ERROR: Running from the wrong directory!")
        print(f"Current dir: {os.getcwd()}")
        print("Please 'cd' into the 'scriptWriter_project_3' folder before running.")
        return

    print("====================================================")
    print("🎬 BROWSER SCRIPT WRITER AI (V1.3) - DEEP RESEARCH")
    print("====================================================\n")

    # User Input
    topic = input("Enter the topic for your documentary: ")
    duration = input("duration of the topic: ")
    if not topic:
        print("❌ No topic entered. Exiting.")
        sys.exit(1)

    # Auto-detect language
    if is_bangla(topic):
        language = "bn"
        print("🌏 Detected Language: Bangla")
    else:
        language = "en"
        print("🌏 Detected Language: English")

    max_retries = 3
    attempt = 1
    result = None

    while attempt <= max_retries:
        print(f"\n🔄 [ATTEMPT {attempt}/{max_retries}] Running pipeline...")

        # Run Pipeline
        pipeline = ResearchPipeline()
        result = pipeline.run(topic, language=language, duration=duration)

        script_content = result.get('script', '')

        # Check for failure in the script
        if "Failed to generate script" in script_content:
            print(f"⚠️ Attempt {attempt} failed to generate a cinematic script.")
            if attempt < max_retries:
                print("🧹 Cleaning up browser session memory for retry...")
                # The browser context is closed by the pipeline finally block
                # We delete the persistent session directory to clear "memory"
                session_dir = "gemini_session"
                if os.path.exists(session_dir):
                    try:
                        shutil.rmtree(session_dir)
                        print(f"✅ Deleted {session_dir}")
                    except Exception as e:
                        print(f"⚠️ Could not delete session directory: {e}")
                attempt += 1
                continue
            else:
                print("🚫 Maximum retries reached. Proceeding with current output.")
                break
        else:
            print("✨ Script generated successfully!")
            break

    # Save Raw Data Fallback
    raw_output_file = os.path.join(OUTPUT_DIR, "rawScript.txt")
    if not os.path.exists("/content/drive") and "/content" in os.getcwd():
        raw_output_file = "rawScript.txt"

    try:
        with open(raw_output_file, "w", encoding="utf-8") as f:
            f.write(f"RAW RESEARCH DATA FOR: {topic}\n")
            f.write("="*50 + "\n\n")

            f.write("--- DEEP ANALYSIS ---\n\n")
            f.write(result.get('deep_analysis', 'Deep analysis failed.'))
            f.write("\n\n" + "="*50 + "\n\n")

            f.write("--- WEB ARTICLES ---\n")
            articles = result.get('raw_data', {}).get('articles', [])
            if not articles:
                f.write("No articles found.\n")
            for art in articles:
                f.write(f"\nTITLE: {art.get('title', 'N/A')}\n")
                f.write(f"URL: {art.get('url', 'N/A')}\n")
                f.write("-" * 20 + "\n")
                f.write(str(art.get('text', 'N/A')) + "\n")
                f.write("=" * 30 + "\n")

            f.write("\n\n--- YOUTUBE DATA ---\n")
            youtube = result.get('raw_data', {}).get('youtube', [])
            if not youtube:
                f.write("No YouTube data found.\n")
            for yt in youtube:
                f.write(f"\nVIDEO: {yt.get('basic', {}).get('title', 'N/A')}\n")
                f.write(f"URL: {yt.get('basic', {}).get('url', 'N/A')}\n")
                f.write(f"UPLOADER: {yt.get('basic', {}).get('channel', 'N/A')}\n")
                f.write(f"DESCRIPTION: {yt.get('metadata', {}).get('description', 'N/A')}\n")
                f.write("-" * 20 + "\n")
                f.write(f"TRANSCRIPT: {yt.get('transcript') or 'No transcript available'}\n")
                f.write("=" * 30 + "\n")
        print(f"📁 Raw research data saved to: {raw_output_file}")
    except Exception as e:
        print(f"⚠️ Could not save rawScript.txt: {e}")

    # Save Output
    output_file = os.path.join(OUTPUT_DIR, "script.txt")

    # Fallback for Colab environment if Drive is not mounted
    if not os.path.exists("/content/drive") and "/content" in os.getcwd():
        print("\n⚠️ WARNING: Google Drive not detected! Saving a copy to local storage for easy download.")
        output_file = "script.txt"

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"TOPIC: {topic}\n")
            f.write("="*50 + "\n\n")
            f.write("--- DEEP ANALYSIS ---\n\n")
            f.write(result['deep_analysis'])
            f.write("\n\n" + "="*50 + "\n\n")
            f.write("--- CINEMATIC SCRIPT ---\n\n")
            f.write(result['script'])
            f.write("\n\n" + "="*50 + "\n")
            f.write("SOURCES:\n")
            for url in result['sources']['articles']:
                f.write(f"- {url}\n")
            for url in result['sources']['videos']:
                f.write(f"- {url}\n")

        print(f"\n✨ SUCCESS! Your script has been saved to: {output_file}")

        # Provide download instructions for Colab if not using Drive
        if not os.path.exists("/content/drive"):
            print("\n📥 To download your script, run this in a new cell:")
            print(f"   from google.colab import files")
            print(f"   files.download('{output_file}')")

    except Exception as e:
        print(f"❌ Error saving script to file: {e}")

if __name__ == "__main__":
    main()
