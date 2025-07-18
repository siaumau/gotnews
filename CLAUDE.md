# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based AI news aggregation and English learning system that fetches AI-related news from NewsAPI and provides intelligent translation and learning features using OpenRouter's AI models. The system features a Flipboard-style card interface for news consumption with integrated language learning capabilities.

## Architecture

### Core Components

1. **Flask Web Application** (`app.py`)
   - Main application server with REST API endpoints
   - Handles news management, translation, and vocabulary operations
   - Serves static templates and provides JSON APIs

2. **Database Layer** (`database.py`)
   - SQLite-based data persistence
   - Manages articles, translations, and vocabulary storage
   - Handles CRUD operations for all entities

3. **News Fetching Service** (`news_fetcher.py`)
   - NewsAPI integration for fetching AI-related news
   - Configurable date ranges and pagination
   - Article deduplication and storage

4. **Translation Service** (`translator.py`)
   - OpenRouter API integration for AI-powered translation
   - Supports bidirectional translation (English ↔ Chinese)
   - Generates learning materials (vocabulary, dialogs, simplified content)

### Database Schema

```sql
-- Main articles table
CREATE TABLE articles (
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
);

-- Vocabulary management
CREATE TABLE vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT,
    meaning TEXT,
    level TEXT,
    source_article_id INTEGER,
    source_article_title TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_article_id) REFERENCES articles (id)
);

-- Translation cache
CREATE TABLE article_translations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER,
    chinese_title TEXT,
    chinese_content TEXT,
    vocabulary TEXT,  -- JSON stored as text
    dialog TEXT,      -- JSON stored as text
    simplified_english TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles (id)
);
```

## API Endpoints

### News Management
- `GET /` - Main application page
- `GET /api/articles` - Fetch all articles (supports favorites filter)
- `POST /api/update` - Fetch new articles from NewsAPI
- `POST /api/articles/<id>/favorite` - Toggle article favorite status
- `DELETE /api/articles/<id>` - Delete article

### Translation & Learning
- `GET /api/articles/<id>/translation-check` - Check if translation exists
- `POST /api/articles/<id>/translate` - Generate translation and learning materials
- `POST /api/clear-translations` - Clear all cached translations

### Vocabulary Management
- `GET /vocabulary` - Vocabulary management page
- `GET /api/vocabulary` - Fetch vocabulary list
- `POST /api/vocabulary` - Add new vocabulary entry
- `DELETE /api/vocabulary/<id>` - Delete vocabulary entry

## Key Features

### 1. News Aggregation
- Fetches AI-related news from NewsAPI
- Stores articles in SQLite database
- Supports article favoriting and management
- Responsive card-based UI inspired by Flipboard

### 2. AI-Powered Translation
- Uses OpenRouter API (DeepSeek model) for translation
- Supports both English-to-Chinese and Chinese-to-English
- Generates learning materials for A1-level English learners
- Caches translations to avoid redundant API calls

### 3. Language Learning Features
- **Vocabulary Extraction**: Identifies key words with difficulty levels (A1/A2/B1)
- **Dialog Generation**: Creates conversational practice materials
- **Simplified English**: Generates A1-level simplified versions
- **Vocabulary Management**: Personal vocabulary notebook with source tracking

### 4. Responsive Frontend
- Modern card-based interface
- Mobile-optimized design
- Real-time updates without page refresh
- Progressive Web App capabilities

## Configuration

### Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Required API Keys
1. **NewsAPI Key**: Required for fetching news articles
   - Get from: https://newsapi.org
   - Free tier: 1,000 requests/day

2. **OpenRouter API Key**: Required for translation features
   - Get from: https://openrouter.ai
   - Pay-per-use model for various AI models

### Security Model
- API keys are stored in browser localStorage (client-side)
- Keys are passed to server via request headers
- No server-side key storage for security

## Development Patterns

### Error Handling
- Comprehensive try-catch blocks in all API endpoints
- Graceful fallback for translation failures
- Unicode encoding issues handled (Windows CP950 codec limitations)

### Database Operations
- Context managers for SQLite connections
- Prepared statements to prevent SQL injection
- Atomic transactions for data consistency

### API Design
- RESTful endpoint structure
- Consistent JSON response format
- Proper HTTP status codes
- CORS-friendly headers

## Known Issues & Solutions

1. **Unicode Encoding**: Windows terminal (CP950) cannot display emoji characters in print statements
   - Error: `UnicodeEncodeError: 'cp950' codec can't encode character`
   - Solution: Use text labels like `[ERROR]`, `[SUCCESS]` instead of emoji in print statements

2. **JSON Parsing**: OpenRouter API responses sometimes contain malformed JSON
   - Implemented robust parsing with fallback mechanisms in `translator.py`
   - Handles markdown code blocks and extra content

3. **Translation Cache**: No automatic cache invalidation
   - Translations are cached indefinitely in `article_translations` table
   - Manual cache clearing available via `/api/clear-translations` endpoint

4. **OpenAI Library**: Import present but not used
   - `requirements.txt` includes openai==1.30.0 but code uses direct requests to OpenRouter
   - Can be safely removed if not needed elsewhere

## Common Commands

### Development Setup
```bash
# Windows - Use provided batch files
setup.bat     # Creates virtual environment and installs dependencies
run.bat       # Activates environment and starts application
show_ip.bat   # Displays network IP addresses for LAN access

# Manual setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run application
python app.py
```

### Testing
```bash
# No formal test suite - manual testing via web interface
# Test translation: http://localhost:5000/api/articles/1/translation-check
# Test news fetch: POST to /api/update with NewsAPI key
```

## Technology Stack

### Backend
- **Flask 2.3.3**: Web framework
- **SQLite**: Database
- **Requests 2.31.0**: HTTP client for API calls
- **OpenAI 1.30.0**: Library dependency (not actually used - replaced with requests)

### Frontend
- **Vanilla JavaScript**: No frameworks
- **CSS3**: Modern styling with flexbox/grid
- **HTML5**: Semantic markup

### External APIs
- **NewsAPI v2**: News aggregation
- **OpenRouter API**: AI translation (DeepSeek model)

## Deployment

### Local Development
```bash
python app.py
# Access: http://localhost:5000
```

### Network Access
```bash
# Application binds to 0.0.0.0:5000
# LAN access: http://192.168.1.100:5000
```

### Production Considerations
1. **Security**: Implement proper authentication
2. **HTTPS**: Use SSL certificates
3. **Rate Limiting**: Implement API rate limiting
4. **Monitoring**: Add logging and monitoring
5. **Scaling**: Consider using PostgreSQL for larger datasets

## File Structure

```
gotnews/
├── app.py                 # Main Flask application
├── database.py            # Database operations
├── news_fetcher.py        # NewsAPI integration
├── translator.py          # OpenRouter API integration
├── requirements.txt       # Python dependencies
├── README.md             # User documentation
├── CLAUDE.md             # Technical documentation (this file)
├── run.bat               # Windows startup script
├── setup.bat             # Windows setup script
├── show_ip.bat           # Network info script
├── templates/
│   ├── index.html        # Main application page
│   └── vocabulary.html   # Vocabulary management page
├── venv/                 # Virtual environment (created by setup)
└── news.db              # SQLite database (created at runtime)
```

## Future Enhancements

1. **User Authentication**: Multi-user support with personal accounts
2. **Advanced Learning**: Spaced repetition algorithms for vocabulary
3. **Speech Integration**: Text-to-speech and speech recognition
4. **Mobile App**: Native mobile application
5. **Analytics**: Learning progress tracking and analytics
6. **Content Expansion**: Support for multiple news categories
7. **Offline Mode**: Progressive Web App with offline capabilities

## Development Patterns

### Error Handling
- Always wrap API calls in try-catch blocks
- Use proper HTTP status codes (400, 404, 500)
- Provide meaningful error messages in JSON responses
- Handle Unicode encoding issues for Windows compatibility

### Database Operations
- Use context managers for SQLite connections
- Implement proper transaction handling
- Use parameterized queries to prevent SQL injection
- Store JSON data as TEXT in SQLite with proper serialization

### API Integration
- Store API keys client-side in localStorage for security
- Pass keys via request JSON body, not headers
- Implement intelligent retry logic for API failures
- Cache expensive operations (translations) to avoid redundant calls

### Frontend Patterns
- Use vanilla JavaScript without frameworks
- Implement responsive design with CSS Grid/Flexbox
- Handle API responses asynchronously with proper error handling
- Use unique IDs for dynamic content to avoid conflicts