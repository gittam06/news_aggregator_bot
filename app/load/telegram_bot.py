import requests
from app.config import settings

# --- THE ROUTER MAP (UPDATED TO THE "BIG 4") ---
# You will replace these placeholder numbers with your actual Telegram Topic IDs
TOPIC_MAP = {
    "Markets & Economy": 3,   # Replace 1111 with actual ID
    "Tech & Innovation": 4,   # Replace 2222 with actual ID
    "Corporate Moves": 5,     # Replace 3333 with actual ID
    "Business Trends": 6      # Replace 4444 with actual ID
}

def send_telegram_message(ai_data: dict, article_link: str):
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    category = ai_data.get('category', 'Business Trends') # Default fallback
    bullets = ai_data.get('bullets', '')
    
    if isinstance(bullets, list):
        bullets = "\n".join(bullets)
        
    message = f"📌 *{category}*\n\n{bullets}\n\n🔗 [Read Full Story]({article_link})"
    
    # Look up the correct Thread ID based on the category
    thread_id = TOPIC_MAP.get(category)
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    if thread_id:
        payload["message_thread_id"] = thread_id
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print(f"✅ Message delivered successfully to '{category}' topic!")
    else:
        print(f"❌ Failed to send message: {response.text}")
        

def send_digest_message(category: str, digest_text: str):
    """
    Sends a combined 'Digest' message containing multiple articles to a specific Topic.
    """
    token = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID
    
    # Look up the correct Thread ID from your map
    thread_id = TOPIC_MAP.get(category)
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": digest_text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True # Set to True so it doesn't load massive link previews
    }
    
    if thread_id:
        payload["message_thread_id"] = thread_id
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print(f"✅ Daily Digest delivered to '{category}' topic!")
    else:
        print(f"❌ Failed to send digest: {response.text}")