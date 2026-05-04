import sys
import os
import time

# Fix Windows terminal encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from app.extract.rss_fetcher import fetch_multiple_feeds
from app.transform.cleaner import clean_news_data
from app.transform.ai_agent import process_article_with_ai
from app.load.telegram_bot import send_digest_message
from app.transform.history import load_seen_links, save_seen_links

# --- RSS Sources (matching run_bot.py production config) ---
sources = {
    "Business & Markets": [
        ("CNBC Top News", "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"),
        ("BBC Business", "https://feeds.bbci.co.uk/news/business/rss.xml"),
        ("MarketWatch", "http://feeds.marketwatch.com/marketwatch/topstories"),
    ],
    "Technology": [
        ("TechCrunch", "https://techcrunch.com/feed/"),
        ("The Verge", "https://www.theverge.com/rss/index.xml"),
        ("Wired", "https://www.wired.com/feed/rss"),
    ],
    "World News": [
        ("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
        ("NPR News", "https://feeds.npr.org/1001/rss.xml"),
        ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    ],
}

# ───── Step 1: Extract ─────
print("1. Extracting from RSS feeds...")
raw_df = fetch_multiple_feeds(sources)

# ───── Step 2: Clean ─────
print("\n2. Cleaning raw data...")
cleaned_df = clean_news_data(raw_df)

if cleaned_df.empty:
    print("⚠️  No articles extracted. Exiting.")
    exit()

# ───── Step 3: Deduplicate using history ─────
print("\n3. Checking history for duplicates...")
seen_links = load_seen_links()
new_articles_df = cleaned_df[~cleaned_df['link'].isin(seen_links)]

# Limit to 10 articles to stay under the free-tier Gemini quota (20 req/day)
ARTICLE_LIMIT = 10
articles_to_process = new_articles_df.head(ARTICLE_LIMIT)

if articles_to_process.empty:
    print("✅ No new stories found. All caught up!")
    exit()

print(f"📰 Found {len(articles_to_process)} new articles to process.\n")

# ───── Step 4: AI Categorization with Retry Logic ─────
print("4. Categorizing articles with Gemini AI...")
categorized_news = {}

for index, article in articles_to_process.iterrows():
    print(f"\n  Reading: {article['title']}")
    
    # Retry logic (matches run_bot.py)
    max_retries = 3
    ai_result = None
    
    for attempt in range(max_retries):
        ai_result = process_article_with_ai(article['title'], article['summary'])
        
        if ai_result is not None:
            break  # Success
        else:
            # ai_agent already waits the API-suggested delay on 429 errors
            print(f"  ⚠️ Retrying... (Attempt {attempt + 1}/{max_retries})")
    
    if ai_result is None:
        print("  ❌ Skipping article after all retries failed.")
        continue
    
    category = ai_result.get('category', 'Business Trends')
    bullets = ai_result.get('bullets', '')
    
    if isinstance(bullets, list):
        bullets = "\n".join(bullets)
    
    if category not in categorized_news:
        categorized_news[category] = []
    
    formatted_story = f"{bullets}\n🔗 [Read More]({article['link']})"
    categorized_news[category].append(formatted_story)
    seen_links.append(article['link'])
    
    # gemini-2.0-flash allows 15 RPM, so 5s gap is safe
    time.sleep(5)

# ───── Step 5: Deliver to Telegram ─────
print("\n\n5. Delivering Digests to Telegram...")
if not categorized_news:
    print("⚠️  No articles were categorized. Nothing to send.")
else:
    for category, stories in categorized_news.items():
        if not stories:
            continue
        
        digest_body = "\n\n".join(stories)
        final_message = f"📰 *{category} Update*\n\n{digest_body}"
        
        send_digest_message(category, final_message)
        time.sleep(3)  # Small pause between Telegram messages

# ───── Step 6: Save history ─────
save_seen_links(seen_links)
print("\n✅ Pipeline test complete! History saved.")