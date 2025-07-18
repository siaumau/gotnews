import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

class NewsFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
    
    def fetch_ai_news(self, from_date: Optional[str] = None) -> List[Dict]:
        if not from_date:
            from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        params = {
            'q': 'AI',
            'from': from_date,
            'sortBy': 'popularity',
            'apiKey': self.api_key,
            'pageSize': 50
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'ok':
                return data['articles']
            else:
                print(f"API Error: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.RequestException as e:
            print(f"Request Error: {e}")
            return []
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return []
    
    def save_articles_to_db(self, database, articles: List[Dict]) -> int:
        saved_count = 0
        for article in articles:
            if database.insert_article(article):
                saved_count += 1
        return saved_count