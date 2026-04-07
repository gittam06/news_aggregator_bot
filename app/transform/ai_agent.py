from google import genai
import json
from app.config import settings

# Initialize the new GenAI client
client = genai.Client(api_key=settings.LLM_API_KEY)

def process_article_with_ai(title: str, content: str) -> dict:
    """
    Sends the article to the LLM to get a categorized, 3-bullet summary.
    """
    prompt = f"""
    You are a professional financial and tech news editor for a busy executive.
    Analyze the following news article:
    Title: {title}
    Content: {content}

    Return a JSON object with EXACTLY two keys:
    1. "category": Choose the single MOST relevant category from this strict list: 
       [
           "Business Trends", "Market Updates", "IPO Updates", 
           "M&A", "Economic Updates", "Startups & VC", 
           "Banking Updates", "Mutual Funds & Insurance", 
           "Tech & FAANG"
       ]
    2. "bullets": A string containing exactly 3 short, punchy bullet points summarizing the news. Use a relevant emoji at the start of each bullet.

    Output ONLY raw JSON. Do not include markdown formatting like ```json.
    """
    
    try:
        # New SDK syntax for generating content
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        # Clean up the response in case the AI adds markdown blocks
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        
        # Convert the string response into a Python dictionary
        structured_data = json.loads(clean_text)
        return structured_data
        
    except Exception as e:
        print(f"❌ AI Processing failed for '{title}': {e}")
        # Return None instead of fake text so we can skip it
        return None