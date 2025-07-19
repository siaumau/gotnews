from flask import Flask, render_template, jsonify, request
from database import NewsDatabase
from news_fetcher import NewsFetcher
from translator import EnglishLearningTranslator
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
db = NewsDatabase()

# API金鑰現在從前端傳遞，不再需要預設值
# fetcher 和 translator 將在需要時動態創建

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/articles')
def get_articles():
    show_favorites = request.args.get('favorites', 'false').lower() == 'true'
    
    if show_favorites:
        articles = db.get_favorite_articles()
    else:
        articles = db.get_all_articles()
    
    return jsonify(articles)

@app.route('/api/update', methods=['POST'])
def update_news():
    try:
        data = request.get_json() or {}
        news_api_key = data.get('news_api_key')
        
        if not news_api_key:
            return jsonify({
                'success': False,
                'message': 'NewsAPI key is required'
            }), 400
        
        # 使用前端提供的API金鑰創建新的fetcher
        temp_fetcher = NewsFetcher(news_api_key)
        articles = temp_fetcher.fetch_ai_news()
        saved_count = temp_fetcher.save_articles_to_db(db, articles)
        
        return jsonify({
            'success': True,
            'message': f'Successfully fetched {len(articles)} articles, saved {saved_count} new articles',
            'saved_count': saved_count,
            'total_fetched': len(articles)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating news: {str(e)}'
        }), 500

@app.route('/api/articles/<int:article_id>/favorite', methods=['POST'])
def toggle_favorite(article_id):
    try:
        success = db.toggle_favorite(article_id)
        if success:
            return jsonify({'success': True, 'message': 'Favorite status updated'})
        else:
            return jsonify({'success': False, 'message': 'Article not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    try:
        success = db.delete_article(article_id)
        if success:
            return jsonify({'success': True, 'message': 'Article deleted'})
        else:
            return jsonify({'success': False, 'message': 'Article not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/articles/<int:article_id>/translation-check', methods=['GET'])
def check_translation(article_id):
    try:
        print(f"[CHECK] Checking translation for article ID: {article_id}")
        # 檢查是否已有翻譯
        existing_translation = db.get_translation(article_id)
        if existing_translation:
            print(f"[FOUND] Found existing translation for article {article_id}")
            return jsonify({
                'exists': True,
                'data': existing_translation
            })
        else:
            print(f"[NEW] No translation found for article {article_id}")
            return jsonify({
                'exists': False
            })
    except Exception as e:
        print(f"[ERROR] Error checking translation for article {article_id}: {e}")
        return jsonify({'exists': False, 'message': str(e)})

@app.route('/api/articles/<int:article_id>/translate', methods=['POST'])
def translate_article(article_id):
    try:
        print(f"[START] Starting translation for article ID: {article_id}")
        data = request.get_json() or {}
        openrouter_api_key = data.get('openrouter_api_key')
        level = data.get('level', 'A3')  # Get level from request, default to A3
        
        if not openrouter_api_key:
            return jsonify({
                'success': False,
                'message': 'OpenRouter API key is required'
            }), 400
        
        # 再次檢查是否已有翻譯（避免重複翻譯）
        existing_translation = db.get_translation(article_id)
        if existing_translation:
            print(f"[CACHED] Using cached translation for article {article_id}")
            return jsonify({
                'success': True,
                'data': existing_translation
            })
        
        # 獲取原文章
        article = db.get_article_by_id(article_id)
        if not article:
            print(f"[ERROR] Article {article_id} not found")
            return jsonify({'success': False, 'message': 'Article not found'}), 404
        
        print(f"[TRANSLATE] Translating article {article_id} for level {level}: {article.get('title', 'No title')[:50]}...")
        
        # 使用前端提供的API金鑰創建新的translator
        temp_translator = EnglishLearningTranslator(openrouter_api_key)
        translation_data = temp_translator.translate_article_for_learning(article, level)
        
        # 儲存翻譯結果
        save_success = db.save_translation(article_id, translation_data)
        print(f"[SAVE] Translation saved for article {article_id}: {save_success}")
        
        return jsonify({
            'success': True,
            'data': translation_data
        })
    except Exception as e:
        print(f"[ERROR] Translation error for article {article_id}: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/vocabulary', methods=['GET'])
def get_vocabulary():
    try:
        vocabulary_list = db.get_vocabulary_list()
        return jsonify(vocabulary_list)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/vocabulary', methods=['POST'])
def add_vocabulary():
    try:
        data = request.json
        success = db.add_vocabulary(
            data['word'],
            data['meaning'],
            data['level'],
            data['source_article_id'],
            data['source_article_title']
        )
        if success:
            return jsonify({'success': True, 'message': 'Vocabulary added'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add vocabulary'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/vocabulary/<int:vocab_id>', methods=['DELETE'])
def delete_vocabulary(vocab_id):
    try:
        success = db.delete_vocabulary(vocab_id)
        if success:
            return jsonify({'success': True, 'message': 'Vocabulary deleted'})
        else:
            return jsonify({'success': False, 'message': 'Vocabulary not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/vocabulary/practice', methods=['POST'])
def practice_vocabulary():
    try:
        data = request.json
        word = data.get('word')
        meaning = data.get('meaning')
        openrouter_api_key = request.headers.get('X-OpenRouter-Api-Key')

        if not openrouter_api_key:
            # Try to get from local storage if not in headers
            # This is a fallback, best to pass from frontend
            # For security reasons, this is not recommended
            pass

        if not word or not meaning:
            return jsonify({'success': False, 'message': 'Word and meaning are required'}), 400

        translator = EnglishLearningTranslator(api_key=openrouter_api_key)
        practice_data = translator.generate_sentence_practice(word, meaning)

        if practice_data.get('error'):
            return jsonify({'success': False, 'message': practice_data.get('error')})

        # Generate HTML for the practice dialogs
        html = ""
        for practice in practice_data.get('practice_dialogs', []):
            html += f"<h4>{practice.get('scenario')}</h4>"
            for line in practice.get('dialog', []):
                # Escape quotes to prevent JavaScript syntax errors
                safe_line = line.get("line", "").replace('"', '&quot;').replace("'", "&#39;")
                html += f'<p><strong>{line.get("speaker")}:</strong> {line.get("line")} <span class="speak-btn" onclick="speakText(\'{safe_line}\')">🔊</span><br><small>{line.get("translation")}</small></p>'
            html += "<hr>"

        return jsonify({'success': True, 'html': html})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/vocabulary')
def vocabulary_page():
    return render_template('vocabulary.html')

@app.route('/api/clear-translations', methods=['POST'])
def clear_translations():
    try:
        with sqlite3.connect(db.db_path) as conn:
            conn.execute("DELETE FROM article_translations")
            conn.commit()
        return jsonify({'success': True, 'message': 'All translations cleared'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)