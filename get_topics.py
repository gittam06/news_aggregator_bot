import requests
from app.config import settings

print("Fetching recent messages from your Telegram Group...")

# Ask Telegram for the latest activity in your group
url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
response = requests.get(url).json()

print("\n--- Recent Messages & Their Topic IDs ---")

# Look at the last 15 messages sent in the group
for result in response.get('result', [])[-15:]: 
    message = result.get('message', {})
    text = message.get('text', 'No text (might be an image or system message)')
    
    # This is the golden key: message_thread_id
    thread_id = message.get('message_thread_id', 'Main Chat (No ID)')
    
    print(f"Message you typed: '{text}' --> Hidden Topic ID: {thread_id}")