import os
import sys
import warnings

# Suppress deprecation warnings for a cleaner output
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Monkeypatch for youtube-search-python + httpx 0.28+ compatibility
# This fixes the "unexpected keyword argument 'proxies'" error by redirecting it to 'proxy'
try:
    import httpx
    def _fix_proxy_kwargs(kwargs):
        if "proxies" in kwargs:
            proxies = kwargs.pop("proxies")
            if isinstance(proxies, dict):
                # httpx 0.28+ expects 'proxy' as a single URL string or a Proxy object
                # youtube-search-python passes a dict like {'http://': ..., 'https://': ...}
                proxy_url = proxies.get("https://") or proxies.get("http://")
                if proxy_url:
                    kwargs["proxy"] = proxy_url
            else:
                kwargs["proxy"] = proxies

    # 1. Patch top-level functions (get, post, etc.)
    _original_methods = {}
    for method_name in ["get", "post", "put", "patch", "delete", "head", "options", "request"]:
        if hasattr(httpx, method_name):
            _original_methods[method_name] = getattr(httpx, method_name)
            def make_patch(name):
                orig = _original_methods[name]
                def patched(*args, **kwargs):
                    _fix_proxy_kwargs(kwargs)
                    return orig(*args, **kwargs)
                return patched
            setattr(httpx, method_name, make_patch(method_name))

    # 2. Patch Client and AsyncClient classes
    for class_name in ["Client", "AsyncClient"]:
        if hasattr(httpx, class_name):
            original_class = getattr(httpx, class_name)
            class PatchedClass(original_class):
                def __init__(self, *args, **kwargs):
                    _fix_proxy_kwargs(kwargs)
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
