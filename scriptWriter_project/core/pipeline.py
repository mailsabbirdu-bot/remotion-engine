from .search import web_search
from .article_extractor import extract_multiple_articles
from .youtube_research import process_youtube_research
import time
from .summarizer import GeminiSummarizer
from .script_writer import ScriptWriter
from .config import MAX_WEB_RESULTS, MAX_YOUTUBE_RESULTS, MAX_WORKERS

class ResearchPipeline:
    def __init__(self, gemini_api_key=None):
        self.summarizer = GeminiSummarizer(api_key=gemini_api_key)
        self.writer = ScriptWriter(api_key=gemini_api_key)

    def run(self, topic, language="en"):
        print(f"\n" + "🚀"*10)
        print(f"🚀 STARTING RESEARCH PIPELINE FOR: '{topic}' (Lang: {language})")
        print("🚀" * 10 + "\n")

        # 1. Web Research
        search_results = web_search(topic, max_results=MAX_WEB_RESULTS)
        urls = [r['url'] for r in search_results]

        # 2. Article Extraction
        articles = extract_multiple_articles(urls, max_workers=MAX_WORKERS)

        # 3. YouTube Research
        youtube_data = process_youtube_research(topic, max_results=MAX_YOUTUBE_RESULTS)

        # 4. Parallel Summarization
        all_summaries = []
        import concurrent.futures
        import random

        def task_wrapper(content, source_type, title, prefix):
            # Small jitter to prevent simultaneous 429s
            time.sleep(random.uniform(0.1, 1.5))
            print(f"   ✍️ Summarizing: {title[:50]}...")
            summary = self.summarizer.summarize_text(content, source_type=source_type)
            return f"{prefix}: {title}\n{summary}"

        tasks = []
        # Prepare Web Article tasks
        for art in articles:
            tasks.append((art['text'], "article", art['title'], "ARTICLE"))

        # Prepare YouTube tasks
        for yt in youtube_data:
            if yt['transcript']:
                tasks.append((yt['transcript'], "video transcript", yt['basic']['title'], "VIDEO"))
            else:
                metadata_text = f"Title: {yt['basic']['title']}\nDescription: {yt['metadata'].get('description', '')}"
                tasks.append((metadata_text, "video metadata", yt['basic']['title'], "VIDEO (METADATA ONLY)"))

        if tasks:
            print(f"\n📝 [SUMMARIZER] Summarizing {len(tasks)} sources in parallel...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                future_to_task = {executor.submit(task_wrapper, *t): t for t in tasks}
                for future in concurrent.futures.as_completed(future_to_task):
                    try:
                        all_summaries.append(future.result())
                    except Exception as e:
                        print(f"❌ Summarization task failed: {e}")

        # 5. Deep Combined Analysis
        deep_analysis = "Deep analysis failed."
        if all_summaries:
            time.sleep(2)
            print(f"\n🧠 Performing Deep Cross-Source Analysis ({language})...")
            try:
                deep_analysis = self.summarizer.deep_combined_analysis(all_summaries, language=language)
            except Exception as e:
                print(f"❌ Deep Analysis Error: {e}")

        # 6. Final Script Generation
        final_script = f"Failed to generate script for {topic}."
        if deep_analysis != "Deep analysis failed.":
            time.sleep(2)
            print(f"\n🎬 Writing Final Documentary Script ({language})...")
            try:
                final_script = self.writer.generate_script(topic, deep_analysis, language=language)
            except Exception as e:
                print(f"❌ Script Writing Error: {e}")

        print("\n✅ PIPELINE COMPLETE!")
        return {
            "topic": topic,
            "deep_analysis": deep_analysis,
            "script": final_script,
            "raw_data": {
                "articles": articles,
                "youtube": youtube_data
            },
            "sources": {
                "articles": [a['url'] for a in articles],
                "videos": [v['basic']['url'] for v in youtube_data]
            }
        }
