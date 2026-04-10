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