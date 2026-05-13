import os
import sys

# Monkeypatch for youtube-search-python + httpx 0.28+ compatibility
# This fixes the "unexpected keyword argument 'proxies'" error by redirecting it to 'proxy'
try:
    import httpx

    # 1. Patch top-level functions (get, post, etc.)
    _original_methods = {}
    for method_name in ["get", "post", "put", "patch", "delete", "head", "options", "request"]:
        if hasattr(httpx, method_name):
            _original_methods[method_name] = getattr(httpx, method_name)

            def make_patch(name):
                orig = _original_methods[name]
                def patched(*args, **kwargs):
                    if "proxies" in kwargs:
                        kwargs["proxy"] = kwargs.pop("proxies")
                    return orig(*args, **kwargs)
                return patched

            setattr(httpx, method_name, make_patch(method_name))

    # 2. Patch Client and AsyncClient classes
    for class_name in ["Client", "AsyncClient"]:
        if hasattr(httpx, class_name):
            original_class = getattr(httpx, class_name)

            class PatchedClass(original_class):
                def __init__(self, *args, **kwargs):
                    if "proxies" in kwargs:
                        kwargs["proxy"] = kwargs.pop("proxies")
                    super().__init__(*args, **kwargs)

            setattr(httpx, class_name, PatchedClass)

except Exception:
    pass

from core.pipeline import ResearchPipeline

# Path discovery for Colab vs Local
DRIVE_BASE = "/content/drive/MyDrive/Counterism_Studio_V4"
LOCAL_BASE = "./Counterism_Studio_V4"
BASE = DRIVE_BASE if os.path.exists("/content/drive") else LOCAL_BASE

OUTPUT_DIR = os.path.join(BASE, "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    # Ensure we are in the project directory
    if not os.path.exists("core/pipeline.py"):
        print("❌ ERROR: Running from the wrong directory!")
        print(f"Current dir: {os.getcwd()}")
        print("Please 'cd' into the 'scriptWriter_project' folder before running.")
        return

    print("====================================================")
    print("🎬 SCRIPT WRITER AI (V1.0) - DEEP RESEARCH")
    print("====================================================\n")

    # User Input
    topic = input("Enter the topic for your documentary: ")
    if not topic:
        print("❌ No topic entered. Exiting.")
        sys.exit(1)

    language = "en"

    # Run Pipeline
    pipeline = ResearchPipeline()
    result = pipeline.run(topic, language=language)

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
