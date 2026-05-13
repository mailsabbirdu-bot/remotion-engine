from duckduckgo_search import DDGS

def is_relevant(text, keywords, threshold=0.3):
    """
    Improved relevance check based on keyword overlap percentage.
    """
    if not text: return False
    text = text.lower()
    found_count = sum(1 for k in keywords if k.lower() in text)
    return (found_count / len(keywords)) >= threshold

def web_search(topic, max_results=10):
    """
    Search the web for a given topic using DuckDuckGo with fallbacks.
    """
    # Augment topic for better relevance if it seems specific to Bangladesh
    search_query = topic
    relevance_keywords = topic.split()

    if "bangladesh" not in topic.lower():
        # Heuristic: if topic is in Bangla or about common BD topics, add Bangladesh
        # We now add it more aggressively to search_query but keep relevance flexible
        if any(ord(c) > 128 for c in topic) or any(k in topic.lower() for k in ["sheikh", "hasina", "dhaka", "taka", "baishakh", "poverty", "economy"]):
            search_query += " Bangladesh"
            if "Bangladesh" not in relevance_keywords: relevance_keywords.append("Bangladesh")

    print(f"\n🔍 [SEARCH] Starting web search for: '{search_query}'")
    results = []

    # 1. Try DuckDuckGo Text Search
    try:
        with DDGS() as ddgs:
            ddgs_gen = ddgs.text(search_query, max_results=max_results * 2) # Get more candidates
            for r in ddgs_gen:
                title = r.get('title', '')
                body = r.get('body', '')
                if is_relevant(title + " " + body, relevance_keywords):
                    results.append({
                        "title": title,
                        "url": r.get('href'),
                        "description": body
                    })
                if len(results) >= max_results: break
        if results:
            print(f"✅ [SEARCH] Successfully fetched {len(results)} results from DuckDuckGo.")
            return results
    except Exception as e:
        print(f"⚠️ DuckDuckGo text search failed: {e}")

    # 2. Try DuckDuckGo News Search (often works when text search fails)
    try:
        print("🔍 [SEARCH] Attempting DuckDuckGo News search...")
        with DDGS() as ddgs:
            ddgs_gen = ddgs.news(search_query, max_results=max_results)
            for r in ddgs_gen:
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
        google_urls = search(search_query, num_results=max_results)
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
