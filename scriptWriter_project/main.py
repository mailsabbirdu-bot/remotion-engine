import os
import sys
from core.pipeline import ResearchPipeline

# Path discovery for Colab vs Local
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

OUTPUT_DIR = os.path.join(BASE, "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    print("====================================================")
    print("🎬 SCRIPT WRITER AI - DEEP RESEARCH & DOCUMENTARY")
    print("====================================================\n")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found!")
        print("Please set the environment variable before running.")
        sys.exit(1)

    # User Input
    topic = input("Enter the topic for your documentary: ")
    if not topic:
        print("❌ No topic entered. Exiting.")
        sys.exit(1)

    # Run Pipeline
    pipeline = ResearchPipeline(gemini_api_key=api_key)
    result = pipeline.run(topic)

    # Save Output
    output_file = os.path.join(OUTPUT_DIR, "script.txt")
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
    except Exception as e:
        print(f"❌ Error saving script to file: {e}")

if __name__ == "__main__":
    main()
