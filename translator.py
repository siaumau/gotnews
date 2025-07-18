from openai import OpenAI
import os
import json
from typing import Dict, List

class EnglishLearningTranslator:
    def __init__(self, api_key=None):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key or 'placeholder_key',
        )
    
    def translate_article_for_learning(self, article: Dict) -> Dict:
        """將文章翻譯成 A1 等級的英文學習內容"""
        
        prompt = f"""
        你是一個專業的英文學習教師。請將以下英文新聞文章改寫成適合 A1 等級學習者的內容，並提供以下功能：

        1. 翻譯標題和內文為中文
        2. 標註出 A1 以上難度的單字（約20%難度提升）
        3. 將內容改寫成兩個人的對話形式，方便練習
        4. 提供重要單字列表及其中文解釋
        5. 使用生活化、日常的英文用語

        原文標題：{article.get('title', '')}
        原文內文：{article.get('description', '')}

        請以JSON格式回應，包含：
        {{
            "chinese_title": "中文標題",
            "chinese_content": "中文內文",
            "vocabulary": [
                {{"word": "單字", "meaning": "中文意思", "level": "A1/A2/B1"}},
                ...
            ],
            "dialog": {{
                "person_a": ["A的對話1", "A的對話2", ...],
                "person_b": ["B的對話1", "B的對話2", ...]
            }},
            "simplified_english": "簡化的英文版本（A1等級）"
        }}
        """
        
        try:
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://gotnews.local",
                    "X-Title": "AI News Learning",
                },
                model="openai/gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_content = completion.choices[0].message.content
            
            # 嘗試解析JSON回應
            try:
                return json.loads(response_content)
            except json.JSONDecodeError:
                # 如果不是JSON格式，返回基本結構
                return {
                    "chinese_title": "翻譯失敗",
                    "chinese_content": "翻譯失敗",
                    "vocabulary": [],
                    "dialog": {"person_a": [], "person_b": []},
                    "simplified_english": response_content
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "chinese_title": "翻譯服務暫時無法使用",
                "chinese_content": "請稍後再試",
                "vocabulary": [],
                "dialog": {"person_a": [], "person_b": []},
                "simplified_english": ""
            }
    
    def create_vocabulary_entry(self, word: str, meaning: str, level: str, article_id: int, article_title: str) -> Dict:
        """創建生字簿條目"""
        return {
            "word": word,
            "meaning": meaning,
            "level": level,
            "source_article_id": article_id,
            "source_article_title": article_title,
            "created_at": None  # 將在資料庫中設定
        }