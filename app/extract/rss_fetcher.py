import feedparser
import requests
import pandas as pd

# Browser-like headers for all requests
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
    "Accept-Language": "en-US,en;q=0.9",
}

def _fetch_single_feed(url, source_name):
    """Fetch and parse a single RSS feed. Returns a list of article dicts."""
    articles = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        print(f"  HTTP {response.status_code} | {len(response.content)} bytes | {source_name}")

        if response.status_code != 200:
            return articles

        feed = feedparser.parse(response.content)

        if feed.bozo and not feed.entries:
            print(f"  ⚠️ Parse error: {feed.bozo_exception}")
            return articles

        for entry in feed.entries:
            articles.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", None),
                "summary": entry.get("summary", "No summary available"),
                "source": source_name,
            })

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Network error: {e}")

    return articles


def fetch_multiple_feeds(feed_urls_dict):
    """
    Takes a dictionary of {Source_Name: RSS_URL} and returns a combined DataFrame.
    Supports both single-URL strings and lists of (label, url) tuples for
    multi-source categories.
    """
    all_articles = []

    for source_name, url_value in feed_urls_dict.items():
        print(f"Fetching news from {source_name}...")

        # Support both "url_string" and [(label, url), ...] formats
        if isinstance(url_value, list):
            for label, url in url_value:
                arts = _fetch_single_feed(url, label)
                all_articles.extend(arts)
                if arts:
                    print(f"  ✅ {len(arts)} articles from {label}")
        else:
            arts = _fetch_single_feed(url_value, source_name)
            all_articles.extend(arts)
            if arts:
                print(f"  ✅ {len(arts)} articles from {source_name}")

    print(f"\nTotal articles fetched: {len(all_articles)}")
    df = pd.DataFrame(all_articles)
    return df