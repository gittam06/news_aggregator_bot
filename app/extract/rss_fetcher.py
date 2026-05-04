import feedparser
import requests
import pandas as pd

# Use a realistic browser User-Agent so Google News doesn't block us
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_multiple_feeds(feed_urls_dict):
    """
    Takes a dictionary of {Source_Name: RSS_URL} and returns a combined Pandas DataFrame.
    Uses requests with a browser User-Agent to avoid being blocked by Google News.
    """
    all_articles = []
    
    for source_name, url in feed_urls_dict.items():
        print(f"Fetching news from {source_name}...")
        
        try:
            # Fetch the RSS XML with a proper User-Agent
            response = requests.get(url, headers=HEADERS, timeout=30)
            print(f"  HTTP {response.status_code} | Content-Length: {len(response.content)} bytes")
            
            if response.status_code != 200:
                print(f"  ⚠️ Non-200 status for {source_name}. Skipping.")
                continue
            
            # Parse the XML content directly (not a URL)
            feed = feedparser.parse(response.content)
            
            if feed.bozo and not feed.entries:
                print(f"  ⚠️ Feed parse error for {source_name}: {feed.bozo_exception}")
                continue
            
            print(f"  ✅ Found {len(feed.entries)} articles from {source_name}")
            
            for entry in feed.entries:
                article = {
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published if hasattr(entry, 'published') else None,
                    "summary": entry.get('summary', 'No summary available'),
                    "source": source_name
                }
                all_articles.append(article)
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Network error fetching {source_name}: {e}")
            continue
            
    print(f"\nTotal articles fetched: {len(all_articles)}")
    df = pd.DataFrame(all_articles)
    return df