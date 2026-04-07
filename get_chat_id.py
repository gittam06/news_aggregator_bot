import requests
from app.config import settings

# 1. Send a message in your Telegram group saying "hello bot"
print("Make sure you just sent a message in your Telegram group!")

# 2. Fetch the updates
url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getUpdates"
response = requests.get(url).json()

try:
    # 3. Extract the chat ID from the latest message
    chat_id = response['result'][-1]['message']['chat']['id']
    chat_title = response['result'][-1]['message']['chat']['title']
    print(f"\n✅ SUCCESS!")
    print(f"Group Name: {chat_title}")
    print(f"Chat ID: {chat_id}")
    print(f"\nNow paste this Chat ID into your .env file!")
except IndexError:
    print("\n❌ Error: No messages found. Go to your Telegram group, say 'hello bot', and run this script again.")
except KeyError:
    print("\n❌ Error: Make sure your TELEGRAM_BOT_TOKEN in .env is correct.")