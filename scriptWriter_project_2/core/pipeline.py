from .search import web_search
from .article_extractor import extract_multiple_articles
from .youtube_research import process_youtube_research
from .browser_automator import BrowserAI
import time
from .summarizer import BrowserSummarizer
from .script_writer import BrowserScriptWriter
from .config import MAX_WEB_RESULTS, MAX_YOUTUBE_RESULTS, MAX_WORKERS

class ResearchPipeline:
    def __init__(self):
        self.browser_ai = BrowserAI(headless=True)
        self.summarizer = BrowserSummarizer(self.browser_ai)
        self.writer = BrowserScriptWriter(self.browser_ai)

    def run(self, topic, language="en"):
        print(f"\n" + "🚀"*10)
        print(f"🚀 STARTING BROWSER-BASED RESEARCH PIPELINE FOR: '{topic}' ({language})")
        print("🚀" * 10 + "\n")

        try:
            # 0. Start Browser
            self.browser_ai.start()

            # 1. Web Research
            search_results = web_search(topic, max_results=MAX_WEB_RESULTS)
            urls = [r['url'] for r in search_results]

            # 2. Article Extraction
            articles = extract_multiple_articles(urls, max_workers=MAX_WORKERS)

            # 3. YouTube Research
            youtube_data = process_youtube_research(topic, max_results=MAX_YOUTUBE_RESULTS, language=language)

            # 4. Summarization (Sequential for browser stability)
            all_summaries = []

            print(f"\n📝 [SUMMARIZER] Summarizing {len(articles)} Web Articles via Browser...")
            for art in articles:
                summary = self.summarizer.summarize_text(art['text'], source_type="article", language=language)
                all_summaries.append(f"ARTICLE: {art['title']}\n{summary}")

            print(f"\n📝 [SUMMARIZER] Summarizing {len(youtube_data)} YouTube Transcripts via Browser...")
            for yt in youtube_data:
                if yt['transcript']:
                    summary = self.summarizer.summarize_text(yt['transcript'], source_type="video transcript", language=language)
                    all_summaries.append(f"VIDEO: {yt['basic']['title']}\n{summary}")
                else:
                    metadata_text = f"Title: {yt['basic']['title']}\nDescription: {yt['metadata'].get('description', '')}"
                    summary = self.summarizer.summarize_text(metadata_text, source_type="video metadata", language=language)
                    all_summaries.append(f"VIDEO (METADATA ONLY): {yt['basic']['title']}\n{summary}")

            # 5. Deep Combined Analysis
            deep_analysis = "Deep analysis failed."
            if all_summaries:
                print(f"\n🧠 [BROWSER] Performing Deep Cross-Source Analysis ({language})...")
                deep_analysis = self.summarizer.deep_combined_analysis(all_summaries, language=language)

            # 6. Final Script Generation
            final_script = f"Failed to generate script for {topic}."
            if deep_analysis and deep_analysis != "Deep analysis failed.":
                print(f"\n🎬 [BROWSER] Writing Final Documentary Script ({language})...")
                final_script = self.writer.generate_script(topic, deep_analysis, language=language)

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
        finally:
            self.browser_ai.close()
