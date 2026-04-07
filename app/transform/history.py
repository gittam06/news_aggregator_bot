# app/transform/history.py
import os
import json

HISTORY_FILE = "seen_articles.json"
MAX_HISTORY = 500  # Only remember the last 500 URLs to keep the bot fast

def load_seen_links() -> list:
    """Loads the history of sent articles."""
    # If the file doesn't exist yet, return an empty list
    if not os.path.exists(HISTORY_FILE):
        return []
        
    with open(HISTORY_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_seen_links(seen_links: list):
    """Saves the updated history to the file."""
    # Keep only the newest 500 links so the file doesn't get massive
    recent_links = seen_links[-MAX_HISTORY:]
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(recent_links, f)