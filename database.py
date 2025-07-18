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