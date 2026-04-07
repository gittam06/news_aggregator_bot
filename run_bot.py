import schedule
import time
from app.extract.rss_fetcher import fetch_multiple_feeds
from app.transform.cleaner import clean_news_data
from app.transform.ai_agent import process_article_with_ai
from app.load.telegram_bot import send_digest_message

# NEW: Import our memory functions
from app.transform.history import load_seen_links, save_seen_links

def job():
    print(f"\n--- Waking up to process news at {time.strftime('%H:%M:%S')} ---")
    
    sources = {
        "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
        "TechCrunch": "https://techcrunch.com/feed/"
        # (Keep your full list of sources here)
    }

    # 1. Extract & Clean
    raw_df = fetch_multiple_feeds(sources)
    cleaned_df = clean_news_data(raw_df)
    
    if cleaned_df.empty:
        print("No articles extracted. Going back to sleep.")
        return

    # ==========================================
    # 🚨 THE NEW MEMORY CHECK 🚨
    # ==========================================
    print("Checking Memory Bank for duplicates...")
    seen_links = load_seen_links()
    
    # Filter the DataFrame: Keep ONLY rows where the 'link' is NOT in our seen_links
    new_articles_df = cleaned_df[~cleaned_df['link'].isin(seen_links)]
    
    if new_articles_df.empty:
        print("No NEW articles since the last run. Going back to sleep.")
        return
        
    print(f"Found {len(new_articles_df)} brand new articles!")
    # ==========================================

    # 2. Synthesize & Group
    categorized_news = {}
    
    # Process only the NEW articles (Top 10 to be safe)
    for index, article in new_articles_df.head(10).iterrows():
        print(f"\nReading: {article['title']}")
        
        ai_result = process_article_with_ai(article['title'], article['summary'])
        
        if ai_result is None:
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
        
        # Add the successfully processed link to our memory list!
        seen_links.append(article['link'])
        
        time.sleep(15) # API Speed Bump

    # 3. Deliver
    print("\nDelivering Digests to Telegram...")
    for category, stories in categorized_news.items():
        if not stories:
            continue
            
        top_3_stories = stories[:3]
        digest_body = "\n\n➖➖➖➖➖➖➖➖➖➖\n\n".join(top_3_stories)
        final_message = f"📰 *Top Trending in {category}*\n\n{digest_body}"
        
        send_digest_message(category, final_message)
        time.sleep(3)
        
    # 4. Save Memory!
    # Overwrite the json file with our newly updated list
    save_seen_links(seen_links)
    print("Memory Bank updated. Batch complete.")