try:
    import lxml_html_clean
    import sys
    sys.modules['lxml.html.clean'] = lxml_html_clean
except ImportError:
    pass

from newspaper import Article
import concurrent.futures

def extract_article_text(url):
    """
    Extract clean text from a given URL using newspaper3k.
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        return {
            "url": url,
            "title": article.title,
            "text": article.text,
            "top_image": article.top_image,
            "publish_date": str(article.publish_date) if article.publish_date else None
        }
    except Exception as e:
        print(f"⚠️ Failed to extract article from {url}: {e}")
        return None

def extract_multiple_articles(urls, max_workers=5):
    """
    Extract text from multiple URLs in parallel.
    """
    print(f"📄 Extracting content from {len(urls)} articles...")
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(extract_article_text, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            res = future.result()
            if res and res.get("text"):
                results.append(res)
    return results

if __name__ == "__main__":
    # Test
    test_urls = ["https://en.wikipedia.org/wiki/OpenAI"]
    articles = extract_multiple_articles(test_urls)
    for a in articles:
        print(f"Title: {a['title']}\nText length: {len(a['text'])}")
