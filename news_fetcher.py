import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

class NewsFetcher:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.everything_url = "https://newsapi.org/v2/everything"
        self.headlines_url = "https://newsapi.org/v2/top-headlines"
    
    def fetch_news(self, news_type: str = "everything", **kwargs) -> List[Dict]:
        """
        通用新聞抓取方法
        
        Args:
            news_type: "everything" 或 "top-headlines"
            **kwargs: 其他參數
                everything: query, from_date, sort_by
                top-headlines: country, category, from_date
        """
        if news_type == "everything":
            return self._fetch_everything_news(**kwargs)
        elif news_type == "top-headlines":
            return self._fetch_headlines_news(**kwargs)
        else:
            print(f"Unknown news type: {news_type}")
            return []
    
    def _fetch_everything_news(self, query: str = "AI", from_date: Optional[str] = None, 
                              sort_by: str = "popularity") -> List[Dict]:
        """抓取搜尋新聞 (Everything API)"""
        if not from_date:
            from_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        params = {
            'q': query,
            'from': from_date,
            'sortBy': sort_by,
            'apiKey': self.api_key,
            'pageSize': 50
        }
        
        return self._make_request(self.everything_url, params)
    
    def _fetch_headlines_news(self, country: str = "us", category: str = "business", 
                             from_date: Optional[str] = None) -> List[Dict]:
        """抓取頭條新聞 (Top Headlines API)"""
        params = {
            'country': country,
            'category': category,
            'apiKey': self.api_key,
            'pageSize': 50
        }
        
        # Top Headlines API 不支援 from 參數，只能用於當前/近期新聞
        # 如果需要歷史新聞，需要使用 Everything API
        
        return self._make_request(self.headlines_url, params)
    
    def _make_request(self, url: str, params: Dict) -> List[Dict]:
        """執行API請求的共用方法"""
        try:
            print(f"[INFO] Fetching news from: {url}")
            print(f"[INFO] Parameters: {dict(params)}")  # 創建副本以避免顯示API金鑰
            params_copy = dict(params)
            params_copy['apiKey'] = '***hidden***'
            print(f"[INFO] Safe parameters: {params_copy}")
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'ok':
                print(f"[SUCCESS] Retrieved {len(data['articles'])} articles")
                return data['articles']
            else:
                print(f"[ERROR] API Error: {data.get('message', 'Unknown error')}")
                return []
                
        except requests.RequestException as e:
            print(f"[ERROR] Request Error: {e}")
            return []
        except Exception as e:
            print(f"[ERROR] Unexpected Error: {e}")
            return []
    
    # 保持向後兼容的方法
    def fetch_ai_news(self, from_date: Optional[str] = None) -> List[Dict]:
        """向後兼容的AI新聞抓取方法"""
        return self.fetch_news("everything", query="AI", from_date=from_date)
    
    def save_articles_to_db(self, database, articles: List[Dict]) -> int:
        saved_count = 0
        for article in articles:
            if database.insert_article(article):
                saved_count += 1
        return saved_count