import json
import os
import re
import time
from datetime import datetime
from google import genai
from app.config import settings

# Configure Gemini API
client = genai.Client(api_key=settings.GEMINI_API_KEY)

# ──── Model Rotation Pool ────
# Each model gets its own free-tier daily quota (RPD).
# We rotate through them automatically when one is exhausted.
MODEL_POOL = [
    {"name": "gemini-2.5-flash-lite", "rpd_limit": 20, "rpm_limit": 10},
    {"name": "gemini-2.5-flash",      "rpd_limit": 20, "rpm_limit": 5},
]

# ──── Usage Tracker ────
USAGE_FILE = "api_usage.json"

def _load_usage() -> dict:
    """Load today's API usage from disk."""
    if not os.path.exists(USAGE_FILE):
        return {}
    with open(USAGE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def _save_usage(usage: dict):
    """Save API usage to disk."""
    with open(USAGE_FILE, "w") as f:
        json.dump(usage, f, indent=2)

def _get_today_key() -> str:
    """Returns today's date string as the usage key."""
    return datetime.now().strftime("%Y-%m-%d")

def _get_model_usage(usage: dict, model_name: str) -> int:
    """Get how many requests have been made to a model today."""
    today = _get_today_key()
    return usage.get(today, {}).get(model_name, 0)

def _increment_model_usage(usage: dict, model_name: str) -> dict:
    """Record one more request to a model for today."""
    today = _get_today_key()
    if today not in usage:
        # New day — reset all counters, keep only today
        usage = {today: {}}
    if model_name not in usage[today]:
        usage[today][model_name] = 0
    usage[today][model_name] += 1
    return usage

def _pick_best_model(usage: dict) -> dict | None:
    """Pick the first model that still has daily quota remaining."""
    for model in MODEL_POOL:
        used = _get_model_usage(usage, model["name"])
        remaining = model["rpd_limit"] - used
        if remaining > 0:
            print(f"  [Model: {model['name']} | Used: {used}/{model['rpd_limit']} RPD]")
            return model
    return None


# ──── Rate Limiter ────
_last_request_time = 0

def _rate_limit_wait(rpm_limit: int):
    """Ensures we never exceed the per-minute request limit."""
    global _last_request_time
    min_delay = 60.0 / rpm_limit + 1  # e.g. 10 RPM → 7s gap
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < min_delay:
        wait_time = min_delay - elapsed
        print(f"  >> Rate limiter: waiting {wait_time:.1f}s...")
        time.sleep(wait_time)
    _last_request_time = time.time()


# ──── Main Function ────
def process_article_with_ai(title: str, summary: str):
    """Sends the article to Gemini with automatic model rotation and rate limiting."""
    
    usage = _load_usage()
    model_info = _pick_best_model(usage)
    
    if model_info is None:
        print("  !! All models exhausted for today. Skipping AI processing.")
        return None
    
    model_name = model_info["name"]
    rpm_limit = model_info["rpm_limit"]
    
    prompt = f"""
    You are an elite financial and tech news editor curating content for a premium Telegram group.
    Read the following article title and summary.

    Article Title: {title}
    Summary: {summary}

    Task 1: Categorize this article into EXACTLY ONE of the following 4 categories:
    1. "Markets & Economy" (Inflation, interest rates, stock market rallies, macroeconomics)
    2. "Tech & Innovation" (AI, Apple/Google news, major startups, software)
    3. "Corporate Moves" (IPO updates, Mergers & Acquisitions, CEO changes)
    4. "Business Trends" (Global trade, supply chain, retail, energy shock)

    Task 2: Write 3 short, punchy bullet points summarizing the article for a fast-paced audience.

    Return ONLY a valid JSON object matching this exact format, with no markdown formatting blocks around it:
    {{
        "category": "Exact Category Name Here",
        "bullets": "• Point 1\\n• Point 2\\n• Point 3"
    }}
    """
    
    # Respect rate limits before making the request
    _rate_limit_wait(rpm_limit)
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        # Success — record the usage
        usage = _increment_model_usage(usage, model_name)
        _save_usage(usage)
        
        response_text = response.text.strip()
        
        # Clean up markdown code blocks if Gemini adds them
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        return json.loads(response_text)
        
    except Exception as e:
        error_msg = str(e)
        print(f"  !! AI error: {error_msg[:200]}")
        
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            # Mark this model as fully used for today so we switch to the next one
            today = _get_today_key()
            if today not in usage:
                usage = {today: {}}
            usage[today][model_name] = model_info["rpd_limit"]  # Max it out
            _save_usage(usage)
            print(f"  >> Marked {model_name} as exhausted. Will switch to next model.")
            
        elif "503" in error_msg or "UNAVAILABLE" in error_msg:
            print("  >> Server busy (503). Will retry shortly...")
        
        return None