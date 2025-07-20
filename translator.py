import os
import json
import requests
from typing import Dict, List

LEVELS = ["A2", "A3", "A4", "A5", "A6", "B1", "B2", "C1"]

def get_target_levels_text(level: str) -> str:
    """
    Given a level, returns a string representing the target learning levels.
    e.g., 'A3' -> 'A3 and A4'
    """
    try:
        level = level.upper()
        current_index = LEVELS.index(level)
        if current_index < len(LEVELS) - 1:
            next_level = LEVELS[current_index + 1]
            return f"{level} and {next_level}"
        else:
            return level
    except ValueError:
        return f"{level} and the next level up"

class EnglishLearningTranslator:
    def __init__(self, api_key=None):
        self.api_key = api_key or 'placeholder_key'
        self.base_url = "https://openrouter.ai/api/v1"

    def detect_language(self, text: str) -> str:
        """檢測文本語言"""
        chinese_chars = len([char for char in text if '\u4e00' <= char <= '\u9fff'])
        total_chars = len(text.replace(' ', ''))

        if total_chars == 0:
            return 'english'

        chinese_ratio = chinese_chars / total_chars
        return 'chinese' if chinese_ratio > 0.3 else 'english'

    def translate_article_for_learning(self, article: Dict, level: str = "A3") -> Dict:
        """智能翻譯文章成學習內容"""

        title = article.get('title', '')
        content = article.get('content', '') or article.get('description', '')

        # 檢測語言
        language = self.detect_language(title + ' ' + content)
        target_levels = get_target_levels_text(level)

        if language == 'chinese':
            # 中文翻譯成英文
            prompt = f"""
            你是專業的英文教師。請將以下中文新聞翻譯成適合 {target_levels} 等級學習者的英文內容。

            原文標題：{title}
            原文內文：{content}

            請嚴格按照以下JSON格式回應：

            {{
                "english_title": "English title translation",
                "english_content": "English content translation",
                "vocabulary": [
                    {{"word": "English word", "meaning": "中文意思", "level": "{level}"}},
                    {{"word": "English word", "meaning": "中文意思", "level": "next level"}}
                ],
                "dialog": {{
                    "person_a": ["English dialog 1", "English dialog 2", "English dialog 3"],
                    "person_b": ["English dialog 1", "English dialog 2", "English dialog 3"]
                }},
                "simplified_english": "Simple English version for {level} learners"
            }}

            重要要求：
            1. vocabulary 必須包含5-7個重要的**英文單字**，並標註它們對應的 {target_levels} 等級。
            2. dialog 必須用簡單的**英文對話**，內容與新聞相關。
            3. simplified_english 是為 {level} 等級學習者準備的簡化版**英文**。
            4. 所有學習內容（vocabulary, dialog, simplified_english）都必須是英文，不可以是中文。
            """
        else:
            # 英文翻譯成中文
            prompt = f"""
            你是專業的英文學習教師。請將以下英文新聞改寫成適合 {target_levels} 等級學習者的中文學習內容。

            原文標題：{title}
            原文內文：{content}

            請嚴格按照以下JSON格式回應：

            {{
                "chinese_title": "中文標題翻譯",
                "chinese_content": "中文內文翻譯",
                "vocabulary": [
                    {{"word": "English word", "meaning": "中文意思", "level": "{level}"}},
                    {{"word": "English word", "meaning": "中文意思", "level": "next level"}}
                ],
                "dialog": {{
                    "person_a": ["A的英文對話1", "A的英文對話2", "A的英文對話3"],
                    "person_b": ["B的英文對話1", "B的英文對話2", "B的英文對話3"]
                }},
                "simplified_english": "簡化的英文版本適合 {level} 等級學習者"
            }}

            重要要求：
            1. 只返回純JSON。
            2. vocabulary 必須包含5-7個重要的**英文單字**，並標註它們對應的 {target_levels} 等級。
            3. dialog 必須用簡單的**英文對話**，內容與新聞相關。
            4. simplified_english 是為 {level} 等級學習者準備的簡化版**英文**。
            5. 所有學習內容（vocabulary, dialog, simplified_english）都必須是英文，不可以是中文。
            """

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://gotnews.local",
                "X-Title": "AI News Learning"
            }

            payload = {
                "model": "meta-llama/llama-3.2-3b-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"API call failed with status {response.status_code}: {response.text}")

            response_data = response.json()
            response_content = response_data['choices'][0]['message']['content']

            # 嘗試解析JSON回應
            try:
                # 清理回應內容，移除可能的markdown代碼塊標記
                cleaned_content = response_content.strip()

                # 多種方式嘗試提取JSON
                json_content = None
                
                # 方法1：尋找```json代碼塊
                if '```json' in cleaned_content:
                    start = cleaned_content.find('```json') + 7
                    end = cleaned_content.find('```', start)
                    if end != -1:
                        json_content = cleaned_content[start:end].strip()
                
                # 方法2：尋找```代碼塊（無json標記）
                elif '```' in cleaned_content and json_content is None:
                    start = cleaned_content.find('```') + 3
                    end = cleaned_content.find('```', start)
                    if end != -1:
                        potential_json = cleaned_content[start:end].strip()
                        # 檢查是否以{開始
                        if potential_json.startswith('{'):
                            json_content = potential_json
                
                # 方法3：直接找第一個{到最後一個}
                if json_content is None:
                    json_start = cleaned_content.find('{')
                    json_end = cleaned_content.rfind('}') + 1
                    if json_start != -1 and json_end != -1 and json_start < json_end:
                        json_content = cleaned_content[json_start:json_end]

                if json_content:
                    # 嘗試修復常見的JSON錯誤
                    json_content = json_content.replace('\n', ' ')  # 移除換行
                    json_content = json_content.replace('\\[', '[')  # 修復轉義
                    json_content = json_content.replace('\\}', '}')  # 修復轉義
                    
                    # 嘗試解析JSON
                    parsed_result = json.loads(json_content)

                    # 確保所有必需的字段都存在，支援中英文兩種格式
                    result = {
                        "chinese_title": parsed_result.get("chinese_title", parsed_result.get("english_title", "翻譯失敗")),
                        "chinese_content": parsed_result.get("chinese_content", parsed_result.get("english_content", "翻譯失敗")),
                        "vocabulary": parsed_result.get("vocabulary", []),
                        "dialog": parsed_result.get("dialog", {"person_a": [], "person_b": []}),
                        "simplified_english": parsed_result.get("simplified_english", ""),
                        "language": language,
                        "is_chinese_source": language == 'chinese'
                    }

                    return result
                else:
                    # 沒有找到有效的JSON結構
                    raise json.JSONDecodeError("No valid JSON structure found", response_content, 0)

            except json.JSONDecodeError as e:
                print(f"[ERROR] JSON parsing failed: {str(e)}")
                print(f"[ERROR] Response content: {response_content[:200]}...")
                
                return {
                    "chinese_title": "JSON解析失敗",
                    "chinese_content": f"API回應解析錯誤。錯誤詳情：{str(e)}",
                    "vocabulary": [],
                    "dialog": {"person_a": [], "person_b": []},
                    "simplified_english": "",
                    "language": language,
                    "is_chinese_source": language == 'chinese',
                    "error": f"JSON解析錯誤: {str(e)}",
                    "raw_response": response_content[:500]  # 保留原始回應的前500字符用於調試
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

    def generate_sentence_practice(self, word: str, meaning: str) -> Dict:
        """為單字產生句子練習對話"""
        prompt = f"""
        你是一位專業的英文老師。請為以下單字產生兩個不同情境的英文對話練習，並提供中文翻譯。

        單字：{word}
        意思：{meaning}

        請嚴格按照以下JSON格式回應：
        {{
            "practice_dialogs": [
                {{
                    "scenario": "情境一的描述",
                    "dialog": [
                        {{"speaker": "A", "line": "English line 1", "translation": "中文翻譯1"}},
                        {{"speaker": "B", "line": "English line 2", "translation": "中文翻譯2"}}
                    ]
                }},
                {{
                    "scenario": "情境二的描述",
                    "dialog": [
                        {{"speaker": "A", "line": "English line 1", "translation": "中文翻譯1"}},
                        {{"speaker": "B", "line": "English line 2", "translation": "中文翻譯2"}}
                    ]
                }}
            ]
        }}
        
        重要要求：
        1. 對話中的 "line" 必須是**英文句子**，不可以是中文。
        2. 每個對話至少包含提供的單字 "{word}" 一次。
        3. 英文句子要簡單易懂，適合英文學習者。
        4. translation 提供準確的中文翻譯。
        """

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://gotnews.local",
                "X-Title": "AI News Learning"
            }

            payload = {
                "model": "meta-llama/llama-3.2-3b-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"API call failed with status {response.status_code}: {response.text}")

            response_data = response.json()
            response_content = response_data['choices'][0]['message']['content']

            # 嘗試解析JSON回應
            try:
                # 清理回應內容，移除可能的markdown代碼塊標記
                cleaned_content = response_content.strip()

                # 尋找JSON開始和結束的位置
                json_start = cleaned_content.find('{')
                json_end = cleaned_content.rfind('}') + 1

                if json_start != -1 and json_end != -1 and json_start < json_end:
                    # 提取純JSON部分
                    json_content = cleaned_content[json_start:json_end]

                    parsed_result = json.loads(json_content)
                    return parsed_result
                else:
                    # 沒有找到有效的JSON結構
                    raise json.JSONDecodeError("No valid JSON structure found", response_content, 0)

            except json.JSONDecodeError as e:
                return {"error": f"JSON解析錯誤: {str(e)}"}

        except Exception as e:
            return {"error": str(e)}
