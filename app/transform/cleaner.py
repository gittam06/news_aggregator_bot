import pandas as pd
import re

def clean_news_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the raw DataFrame before sending it to the AI."""
    print("Cleaning raw data...")
    
    # CRITICAL FIX: Check if the DataFrame is empty first
    if df.empty:
        print("Warning: No data was extracted. Skipping cleaning.")
        return df
    
    # 1. Drop articles with missing titles or links
    df = df.dropna(subset=['title', 'link'])
    
    # 2. Drop duplicate articles
    df = df.drop_duplicates(subset=['title'], keep='first')
    df = df.drop_duplicates(subset=['link'], keep='first')
    
    # 3. Clean up the text
    def remove_html(text):
        if not isinstance(text, str):
            return text
        clean = re.compile('<.*?>')
        return re.sub(clean, '', text)

    df['summary'] = df['summary'].apply(remove_html)
    
    print(f"Data cleaned. {len(df)} unique articles ready for processing.")
    return df