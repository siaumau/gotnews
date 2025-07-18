# 🔍 AI 新聞資料抓取與呈現系統

仿 Flipboard 卡片式介面的 AI 新聞聚合系統，透過 NewsAPI 抓取最新 AI 相關新聞。

## 功能特色

- 📱 Flipboard 風格的響應式卡片介面
- 🔄 一鍵更新最新 AI 新聞
- ⭐ 收藏/取消收藏功能
- 🗑️ 刪除不需要的文章
- 📊 SQLite 資料庫儲存
- 🔍 收藏列表篩選
- 📚 **A1 英文學習功能**
- 🌍 **AI 翻譯與簡化**
- 💬 **對話練習模式**
- 📖 **生字簿管理**

## 安裝說明

1. 安裝依賴套件：
```bash
pip install -r requirements.txt
```

2. 執行應用程式：
```bash
python app.py
```

3. 開啟瀏覽器訪問：`http://localhost:5000`

4. 初次設定 API 金鑰：
   - 首次開啟系統會自動顯示設定頁面
   - 輸入你的 NewsAPI 金鑰（必填）
   - 選擇性輸入 OpenRouter API 金鑰（用於翻譯功能）
   - 金鑰會安全儲存在瀏覽器的 localStorage 中

## API 金鑰申請

### NewsAPI
1. 訪問 [NewsAPI](https://newsapi.org)
2. 註冊免費帳號
3. 獲取 API 金鑰

### OpenRouter (用於 AI 翻譯)
1. 訪問 [OpenRouter](https://openrouter.ai)
2. 註冊帳號
3. 獲取 API 金鑰
4. 在網頁介面中輸入金鑰

## 管理 API 金鑰

- **查看/修改金鑰**：點擊頁面上的「⚙️ 設定」按鈕
- **安全性**：金鑰儲存在瀏覽器 localStorage 中，不會傳送到伺服器
- **更換金鑰**：可隨時在設定頁面更新金鑰
- **清除金鑰**：可在設定頁面清除所有金鑰

## 使用方式

### 基本功能
- **更新新聞**：點擊「🔄 更新新聞」按鈕
- **收藏文章**：點擊文章卡片上的「⭐」按鈕
- **刪除文章**：點擊「🗑️」按鈕
- **查看收藏**：點擊「⭐ 我的收藏」按鈕
- **閱讀原文**：點擊「閱讀原文 →」連結

### 英文學習功能
- **開始學習**：點擊文章卡片上的「📚」按鈕
- **查看翻譯**：AI 自動翻譯文章為中文
- **練習對話**：查看改寫的雙人對話練習
- **學習單字**：檢視 A1 等級重點單字
- **加入生字簿**：點擊「加入生字簿」按鈕
- **管理生字簿**：點擊「📚 生字簿」查看已收藏的單字

## 檔案結構

```
gotnews/
├── app.py              # Flask 主應用程式
├── database.py         # SQLite 資料庫操作
├── news_fetcher.py     # NewsAPI 資料抓取
├── translator.py       # AI 翻譯與學習功能
├── requirements.txt    # Python 依賴套件
├── templates/
│   ├── index.html     # 主頁面（新聞列表）
│   └── vocabulary.html # 生字簿頁面
└── news.db            # SQLite 資料庫檔案（自動建立）
```

## 技術規格

- **後端**：Python Flask
- **資料庫**：SQLite
- **前端**：原生 HTML/CSS/JavaScript
- **API**：NewsAPI v2, OpenRouter API
- **AI 模型**：GPT-4o (透過 OpenRouter)
- **響應式設計**：支援桌面與行動裝置

## 新功能說明

### 英文學習系統
- **A1 等級設計**：專為英文初學者設計，提供適合 A1 水平的學習內容
- **智能翻譯**：使用 GPT-4o 進行文章翻譯與簡化
- **對話練習**：將新聞內容改寫為雙人對話，便於口語練習
- **生字管理**：自動標註重點單字，可加入個人生字簿
- **來源追蹤**：每個單字都會記錄來源文章，便於複習

### 資料庫結構
- **articles**：新聞文章資料
- **vocabulary**：生字簿資料
- **article_translations**：文章翻譯快取