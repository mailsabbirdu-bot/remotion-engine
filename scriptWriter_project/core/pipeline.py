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

        # 4. Summarization
        all_summaries = []

        print(f"\n📝 [SUMMARIZER] Summarizing {len(articles)} Web Articles...")
        for i, art in enumerate(articles):
            if i > 0:
                time.sleep(5) # Delay between summaries
            print(f"   ✍️ Summarizing: {art['title'][:50]}...")
            summary = self.summarizer.summarize_text(art['text'], source_type="article")
            all_summaries.append(f"ARTICLE: {art['title']}\n{summary}")

        print(f"\n📝 [SUMMARIZER] Summarizing {len(youtube_data)} YouTube Transcripts...")
        for i, yt in enumerate(youtube_data):
            if i > 0 or articles:
                time.sleep(5)
            if yt['transcript']:
                summary = self.summarizer.summarize_text(yt['transcript'], source_type="video transcript")
                all_summaries.append(f"VIDEO: {yt['basic']['title']}\n{summary}")
            else:
                # Use metadata if no transcript
                metadata_text = f"Title: {yt['basic']['title']}\nDescription: {yt['metadata'].get('description', '')}"
                summary = self.summarizer.summarize_text(metadata_text, source_type="video metadata")
                all_summaries.append(f"VIDEO (METADATA ONLY): {yt['basic']['title']}\n{summary}")

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
