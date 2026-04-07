import time # Add this at the very top of the file!
from app.extract.rss_fetcher import fetch_multiple_feeds
from app.transform.cleaner import clean_news_data
from app.transform.ai_agent import process_article_with_ai
from app.load.telegram_bot import send_digest_message

sources = {
    "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
    "Hacker News": "https://news.ycombinator.com/rss",
    "TechCrunch": "https://techcrunch.com/feed/",
    "Renaissance Capital (IPOs)": "https://www.renaissancecapital.com/feed/ipo",
    "Reuters M&A": "https://www.reutersagency.com/feed/?best-topics=mergers-acquisitions&post_type=best",
    "Banking Dive": "https://www.bankingdive.com/feeds/news/",
    "Morningstar (Funds)": "https://www.morningstar.com/rss/all",
    "VentureBeat": "https://feeds.feedburner.com/venturebeat/SZYF",
    "Crunchbase News": "https://news.crunchbase.com/feed/",
}

print("1. Extracting...")
raw_df = fetch_multiple_feeds(sources)

print("2. Cleaning...")
cleaned_df = clean_news_data(raw_df)

print("3. Synthesizing & Grouping with AI...")
categorized_news = {}

for index, article in cleaned_df.head(10).iterrows():
    print(f"\nReading: {article['title']}")
    
    ai_result = process_article_with_ai(article['title'], article['summary'])
    
    # NEW: If the AI failed (rate limit, json error), skip this article completely
    if ai_result is None:
        print("Skipping article due to AI error. Pausing before next attempt...")
        time.sleep(15) 
        continue
        
    category = ai_result.get('category', 'Business Trends')
    bullets = ai_result.get('bullets', '')
    
    if isinstance(bullets, list):
        bullets = "\n".join(bullets)
    
    if category not in categorized_news:
        categorized_news[category] = []
        
    formatted_story = f"{bullets}\n🔗 [Read Full Story]({article['link']})"
    categorized_news[category].append(formatted_story)
    
    # NEW: The Speed Bump! Pause for 15 seconds to avoid the 429 Rate Limit
    print("Sleeping for 15 seconds to respect API limits...")
    time.sleep(15)

print("\n4. Delivering Digests to Telegram...")
for category, stories in categorized_news.items():
    # Only send if we actually have stories (avoids empty messages)
    if not stories:
        continue
        
    top_3_stories = stories[:3]
    digest_body = "\n\n➖➖➖➖➖➖➖➖➖➖\n\n".join(top_3_stories)
    final_message = f"📰 *Top Trending in {category}*\n\n{digest_body}"
    
    send_digest_message(category, final_message)
    
    # Small pause between sending Telegram messages too
    time.sleep(3)