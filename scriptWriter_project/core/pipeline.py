from .search import web_search
from .article_extractor import extract_multiple_articles
from .youtube_research import process_youtube_research
from .summarizer import GeminiSummarizer
from .script_writer import ScriptWriter
from .config import MAX_WEB_RESULTS, MAX_YOUTUBE_RESULTS, MAX_WORKERS

class ResearchPipeline:
    def __init__(self, gemini_api_key=None):
        self.summarizer = GeminiSummarizer(api_key=gemini_api_key)
        self.writer = ScriptWriter(api_key=gemini_api_key)

    def run(self, topic):
        print(f"\n" + "🚀"*10)
        print(f"🚀 STARTING RESEARCH PIPELINE FOR: '{topic}'")
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
        for art in articles:
            print(f"   ✍️ Summarizing: {art['title'][:50]}...")
            summary = self.summarizer.summarize_text(art['text'], source_type="article")
            all_summaries.append(f"ARTICLE: {art['title']}\n{summary}")

        print(f"\n📝 [SUMMARIZER] Summarizing {len(youtube_data)} YouTube Transcripts...")
        for yt in youtube_data:
            if yt['transcript']:
                summary = self.summarizer.summarize_text(yt['transcript'], source_type="video transcript")
                all_summaries.append(f"VIDEO: {yt['basic']['title']}\n{summary}")
            else:
                # Use metadata if no transcript
                metadata_text = f"Title: {yt['basic']['title']}\nDescription: {yt['metadata'].get('description', '')}"
                summary = self.summarizer.summarize_text(metadata_text, source_type="video metadata")
                all_summaries.append(f"VIDEO (METADATA ONLY): {yt['basic']['title']}\n{summary}")

        # 5. Deep Combined Analysis
        print("\n🧠 Performing Deep Cross-Source Analysis...")
        deep_analysis = self.summarizer.deep_combined_analysis(all_summaries)

        # 6. Final Script Generation
        print("\n🎬 Writing Final Documentary Script...")
        final_script = self.writer.generate_script(topic, deep_analysis)

        print("\n✅ PIPELINE COMPLETE!")
        return {
            "topic": topic,
            "deep_analysis": deep_analysis,
            "script": final_script,
            "sources": {
                "articles": [a['url'] for a in articles],
                "videos": [v['basic']['url'] for v in youtube_data]
            }
        }
