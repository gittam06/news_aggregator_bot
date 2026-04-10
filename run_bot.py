import os
import time
from fastapi import FastAPI, BackgroundTasks
import uvicorn

from app.extract.rss_fetcher import fetch_multiple_feeds
from app.transform.cleaner import clean_news_data
from app.transform.ai_agent import process_article_with_ai
from app.load.telegram_bot import send_digest_message
from app.transform.history import load_seen_links, save_seen_links

app = FastAPI()

def job():
    print(f"\n--- Waking up for scheduled briefing at {time.strftime('%H:%M:%S')} ---")
    
    # 1. Fetch & Clean (UPDATED TO GOOGLE NEWS AGGREGATORS)
    sources = {
        "Google Business & Markets": "https://news.google.com/rss/headlines/section/topic/BUSINESS?hl=en-US&gl=US&ceid=US:en",
        "Google Technology": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en",
        "Google Top World News": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en"
    }
    raw_df = fetch_multiple_feeds(sources)
    cleaned_df = clean_news_data(raw_df)
    
    if cleaned_df.empty:
        return

    # 2. Memory Check
    seen_links = load_seen_links()
    new_articles_df = cleaned_df[~cleaned_df['link'].isin(seen_links)]
    
    # CRITICAL: We limit to 10 articles to stay under the 20/day Google limit
    limit = 10 
    articles_to_process = new_articles_df.head(limit)
    
    if articles_to_process.empty:
        print("No new stories found.")
        return
        
    print(f"Processing {len(articles_to_process)} top stories...")

    categorized_news = {}
    for index, article in articles_to_process.iterrows():
        
        # --- RETRY LOGIC ---
        max_retries = 3
        ai_result = None
        
        for attempt in range(max_retries):
            ai_result = process_article_with_ai(article['title'], article['summary'])
            
            if ai_result is not None:
                break # Success! Break out of the retry loop.
            else:
                print(f"⚠️ API Busy. Retrying in 10 seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(10) # Wait 10 seconds before asking Google again
        # ---------------------------
        
        if ai_result:
            category = ai_result.get('category', 'General News')
            bullets = ai_result.get('bullets', '')
            if category not in categorized_news:
                categorized_news[category] = []
            
            story_text = f"{bullets}\n🔗 [Read More]({article['link']})"
            categorized_news[category].append(story_text)
            seen_links.append(article['link'])
        
        print(f"Processed article. Sleeping for 15 seconds to respect API limits...")
        time.sleep(15)

    # 3. Send to Telegram
    for category, stories in categorized_news.items():
        digest = "\n\n".join(stories)
        final_msg = f"📰 *{category} Update*\n\n{digest}"
        send_digest_message(category, final_msg)
    
    save_seen_links(seen_links)
    print("Briefing complete.")

# --- THE WEB SERVER ROUTES ---

@app.get("/")
def keep_awake():
    """This route just keeps the server from going to sleep."""
    return {"status": "Bot is awake and listening!"}

@app.get("/trigger-news")
def trigger_news(background_tasks: BackgroundTasks):
    """When this URL is visited, it runs your job in the background!"""
    background_tasks.add_task(job)
    return {"message": "News scraping initiated!"}

if __name__ == "__main__":
    # Render assigns a random port, this catches it automatically
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)