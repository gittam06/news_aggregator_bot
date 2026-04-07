import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Settings:
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Create an instance to import into other files
settings = Settings()