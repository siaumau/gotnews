import sqlite3
from typing import List, Dict, Optional

class NewsDatabase:
    def __init__(self, db_path: str = "news.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT,
                    author TEXT,
                    title TEXT UNIQUE,
                    description TEXT,
                    url TEXT,
                    urlToImage TEXT,
                    publishedAt TEXT,
                    content TEXT,
                    is_favorite INTEGER DEFAULT 0
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vocabulary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT,
                    meaning TEXT,
                    level TEXT,
                    source_article_id INTEGER,
                    source_article_title TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_article_id) REFERENCES articles (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS article_translations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id INTEGER,
                    chinese_title TEXT,
                    chinese_content TEXT,
                    vocabulary TEXT,
                    dialog TEXT,
                    simplified_english TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles (id)
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sentence_practice (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT,
                    meaning TEXT,
                    practice_data TEXT,
                    source_vocabulary_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_vocabulary_id) REFERENCES vocabulary (id)
                )
            """)
            
            conn.commit()
    
    def insert_article(self, article: Dict) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO articles 
                    (source_name, author, title, description, url, urlToImage, publishedAt, content)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article.get('source', {}).get('name'),
                    article.get('author'),
                    article.get('title'),
                    article.get('description'),
                    article.get('url'),
                    article.get('urlToImage'),
                    article.get('publishedAt'),
                    article.get('content')
                ))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False
    
    def get_all_articles(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM articles ORDER BY publishedAt DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_favorite_articles(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM articles WHERE is_favorite = 1 ORDER BY publishedAt DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def toggle_favorite(self, article_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("UPDATE articles SET is_favorite = 1 - is_favorite WHERE id = ?", (article_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_article(self, article_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM articles WHERE id = ?", (article_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_article_by_id(self, article_id: int) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def save_translation(self, article_id: int, translation_data: Dict) -> bool:
        try:
            import json
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO article_translations 
                    (article_id, chinese_title, chinese_content, vocabulary, dialog, simplified_english)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    article_id,
                    translation_data.get('chinese_title'),
                    translation_data.get('chinese_content'),
                    json.dumps(translation_data.get('vocabulary', []), ensure_ascii=False),
                    json.dumps(translation_data.get('dialog', {}), ensure_ascii=False),
                    translation_data.get('simplified_english')
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving translation: {e}")
            return False
    
    def get_translation(self, article_id: int) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM article_translations WHERE article_id = ?", (article_id,))
            row = cursor.fetchone()
            if row:
                import json
                result = dict(row)
                try:
                    # 使用json.loads代替eval，更安全
                    if isinstance(result['vocabulary'], str):
                        result['vocabulary'] = json.loads(result['vocabulary'])
                    if isinstance(result['dialog'], str):
                        result['dialog'] = json.loads(result['dialog'])
                except (json.JSONDecodeError, TypeError):
                    result['vocabulary'] = []
                    result['dialog'] = {"person_a": [], "person_b": []}
                return result
            return None
    
    def add_vocabulary(self, word: str, meaning: str, level: str, source_article_id: int, source_article_title: str) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO vocabulary (word, meaning, level, source_article_id, source_article_title)
                    VALUES (?, ?, ?, ?, ?)
                """, (word, meaning, level, source_article_id, source_article_title))
                conn.commit()
                return True
        except Exception:
            return False
    
    def get_vocabulary_list(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM vocabulary ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_vocabulary(self, vocab_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM vocabulary WHERE id = ?", (vocab_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def save_sentence_practice(self, word: str, meaning: str, practice_data: Dict, source_vocabulary_id: int) -> bool:
        try:
            import json
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO sentence_practice 
                    (word, meaning, practice_data, source_vocabulary_id)
                    VALUES (?, ?, ?, ?)
                """, (
                    word,
                    meaning,
                    json.dumps(practice_data, ensure_ascii=False),
                    source_vocabulary_id
                ))
                conn.commit()
                return True
        except Exception as e:
            print(f"Error saving sentence practice: {e}")
            return False
    
    def get_sentence_practice(self, word: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM sentence_practice WHERE word = ?", (word,))
            row = cursor.fetchone()
            if row:
                import json
                result = dict(row)
                try:
                    if isinstance(result['practice_data'], str):
                        result['practice_data'] = json.loads(result['practice_data'])
                except (json.JSONDecodeError, TypeError):
                    result['practice_data'] = {}
                return result
            return None
    
    def get_all_sentence_practices(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM sentence_practice ORDER BY created_at DESC")
            practices = []
            for row in cursor.fetchall():
                import json
                result = dict(row)
                try:
                    if isinstance(result['practice_data'], str):
                        result['practice_data'] = json.loads(result['practice_data'])
                except (json.JSONDecodeError, TypeError):
                    result['practice_data'] = {}
                practices.append(result)
            return practices
    
    def clear_translations(self) -> bool:
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM article_translations")
                conn.commit()
                return True
        except Exception:
            return False
    
    def delete_sentence_practice(self, practice_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM sentence_practice WHERE id = ?", (practice_id,))
            conn.commit()
            return cursor.rowcount > 0