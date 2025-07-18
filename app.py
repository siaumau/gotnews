from flask import Flask, render_template, jsonify, request
from database import NewsDatabase
from news_fetcher import NewsFetcher
import os
from datetime import datetime

app = Flask(__name__)
db = NewsDatabase()

NEWS_API_KEY = os.getenv('NEWS_API_KEY', 'ABC')
fetcher = NewsFetcher(NEWS_API_KEY)

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
        articles = fetcher.fetch_ai_news()
        saved_count = fetcher.save_articles_to_db(db, articles)
        
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

if __name__ == '__main__':
    app.run(debug=True)