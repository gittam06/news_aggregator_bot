import feedparser
import pandas as pd

def fetch_multiple_feeds(feed_urls_dict):
    """
    Takes a dictionary of {Source_Name: RSS_URL} and returns a combined Pandas DataFrame.
    """
    all_articles = []
    
    for source_name, url in feed_urls_dict.items():
        print(f"Fetching news from {source_name}...")
        feed = feedparser.parse(url)
        
        for entry in feed.entries:
            article = {
                "title": entry.title,
                "link": entry.link,
                "published": entry.published if hasattr(entry, 'published') else None,
                "summary": entry.get('summary', 'No summary available'),
                "source": source_name
            }
            all_articles.append(article)
            
    df = pd.DataFrame(all_articles)
    return df