import json
import google.generativeai as genai
from app.config import settings

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

# Using the fast model you have been using in the logs
model = genai.GenerativeModel('gemini-2.5-flash')

def process_article_with_ai(title: str, summary: str):
    """Sends the article to Gemini and forces it to return JSON for the Big 4 categories."""
    
    # The prompt MUST be inside the function to access the title and summary variables
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
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up the response in case Gemini accidentally adds markdown code blocks (```json ... ```)
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        return json.loads(response_text)
        
    except Exception as e:
        print(f"❌ AI Processing error: {e}")
        return None