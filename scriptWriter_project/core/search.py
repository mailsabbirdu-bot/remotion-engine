from duckduckgo_search import DDGS

def is_relevant(text, keywords, threshold=0.4):
    """
    Improved relevance check based on keyword overlap percentage.
    Filters out common stop words to ensure accuracy.
    """
    if not text: return False

    # Common English stop words to ignore in relevance check
    stop_words = {
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'then', 'else', 'of', 'at', 'by',
        'from', 'for', 'with', 'in', 'on', 'to', 'is', 'are', 'was', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'about', 'most',
        'more', 'very', 'than', 'some', 'any', 'each', 'all', 'such', 'only', 'own'
    }

    clean_keywords = [k.lower() for k in keywords if k.lower() not in stop_words and len(k) > 1]
    if not clean_keywords: clean_keywords = [k.lower() for k in keywords] # Fallback if all are stop words
    if not clean_keywords: return False

    text = text.lower()
    found_count = sum(1 for k in clean_keywords if k in text)
    return (found_count / len(clean_keywords)) >= threshold

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
            # Using the recommended DDGS text search parameters
            ddgs_gen = ddgs.text(search_query, max_results=max_results * 2)
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
