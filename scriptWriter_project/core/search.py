from duckduckgo_search import DDGS

def web_search(topic, max_results=10):
    """
    Search the web for a given topic using DuckDuckGo with fallbacks.
    """
    print(f"\n🔍 [SEARCH] Starting web search for: '{topic}'")
    results = []

    # 1. Try DuckDuckGo Text Search
    try:
        with DDGS() as ddgs:
            ddgs_gen = ddgs.text(topic, max_results=max_results)
            for i, r in enumerate(ddgs_gen, 1):
                results.append({
                    "title": r.get('title'),
                    "url": r.get('href'),
                    "description": r.get('body')
                })
        if results:
            print(f"✅ [SEARCH] Successfully fetched {len(results)} results from DuckDuckGo.")
            return results
    except Exception as e:
        print(f"⚠️ DuckDuckGo text search failed: {e}")

    # 2. Try DuckDuckGo News Search (often works when text search fails)
    try:
        print("🔍 [SEARCH] Attempting DuckDuckGo News search...")
        with DDGS() as ddgs:
            ddgs_gen = ddgs.news(topic, max_results=max_results)
            for i, r in enumerate(ddgs_gen, 1):
                results.append({
                    "title": r.get('title'),
                    "url": r.get('url'),
                    "description": r.get('body')
                })
        if results:
            print(f"✅ [SEARCH] Successfully fetched {len(results)} results from DuckDuckGo News.")
            return results
    except Exception as e:
        print(f"⚠️ DuckDuckGo news search failed: {e}")

    # 3. Try Google Search as final fallback
    try:
        print("🔍 [SEARCH] Attempting Google Search fallback...")
        from googlesearch import search
        # googlesearch-python returns a generator of URLs
        google_urls = search(topic, num_results=max_results)
        for url in google_urls:
            results.append({
                "title": "Web Article",
                "url": url,
                "description": ""
            })
        if results:
            print(f"✅ [SEARCH] Successfully fetched {len(results)} results from Google.")
            return results
    except Exception as e:
        print(f"❌ Google search fallback failed: {e}")

    return results

if __name__ == "__main__":
    # Test
    test_results = web_search("History of OpenAI", max_results=5)
    for res in test_results:
        print(f"- {res['title']} ({res['url']})")
