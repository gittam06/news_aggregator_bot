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
    print(f"\n--- Waking up to process news at {time.strftime('%H:%M:%S')} ---")
    
    sources = {
        "Yahoo Finance": "https://finance.yahoo.com/news/rssindex",
        "TechCrunch": "https://techcrunch.com/feed/"
        # (Add your other sources back here)
    }

    raw_df = fetch_multiple_feeds(sources)
    cleaned_df = clean_news_data(raw_df)
    
    if cleaned_df.empty:
        print("No articles extracted.")
        return

    seen_links = load_seen_links()
    new_articles_df = cleaned_df[~cleaned_df['link'].isin(seen_links)]
    
    if new_articles_df.empty:
        print("No NEW articles.")
        return
        
    categorized_news = {}
    
    for index, article in new_articles_df.head(10).iterrows():
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
        seen_links.append(article['link'])
        time.sleep(15) 

    for category, stories in categorized_news.items():
        if not stories:
            continue
            
        top_3_stories = stories[:3]
        digest_body = "\n\n➖➖➖➖➖➖➖➖➖➖\n\n".join(top_3_stories)
        final_message = f"📰 *Top Trending in {category}*\n\n{digest_body}"
        
        send_digest_message(category, final_message)
        time.sleep(3)
        
    save_seen_links(seen_links)
    print("Batch complete.")

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