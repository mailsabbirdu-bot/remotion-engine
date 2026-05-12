from duckduckgo_search import DDGS

def web_search(topic, max_results=10):
    """
    Search the web for a given topic using DuckDuckGo.
    Returns a list of dictionaries containing title, href (URL), and body (snippet).
    """
    print(f"🔍 Searching the web for: {topic}...")
    results = []
    try:
        with DDGS() as ddgs:
            ddgs_gen = ddgs.text(topic, max_results=max_results)
            for r in ddgs_gen:
                results.append({
                    "title": r.get("title"),
                    "url": r.get("href"),
                    "description": r.get("body")
                })
    except Exception as e:
        print(f"❌ Error during web search: {e}")

    return results

if __name__ == "__main__":
    # Test
    test_results = web_search("History of OpenAI", max_results=5)
    for res in test_results:
        print(f"- {res['title']} ({res['url']})")
