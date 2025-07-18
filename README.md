# 🔍 AI 新聞資料抓取與呈現系統

仿 Flipboard 卡片式介面的 AI 新聞聚合系統，透過 NewsAPI 抓取最新 AI 相關新聞。

## 功能特色

- 📱 Flipboard 風格的響應式卡片介面
- 🔄 一鍵更新最新 AI 新聞
- ⭐ 收藏/取消收藏功能
- 🗑️ 刪除不需要的文章
- 📊 SQLite 資料庫儲存
- 🔍 收藏列表篩選

## 安裝說明

1. 安裝依賴套件：
```bash
pip install -r requirements.txt
```

2. 設定 NewsAPI 金鑰：
```bash
# Windows
set NEWS_API_KEY=your_api_key_here

# Linux/Mac
export NEWS_API_KEY=your_api_key_here
```

3. 執行應用程式：
```bash
python app.py
```

4. 開啟瀏覽器訪問：`http://localhost:5000`

## API 金鑰申請

1. 訪問 [NewsAPI](https://newsapi.org)
2. 註冊免費帳號
3. 獲取 API 金鑰
4. 設定為環境變數

## 使用方式

- **更新新聞**：點擊「🔄 更新新聞」按鈕
- **收藏文章**：點擊文章卡片上的「⭐」按鈕
- **刪除文章**：點擊「🗑️」按鈕
- **查看收藏**：點擊「⭐ 我的收藏」按鈕
- **閱讀原文**：點擊「閱讀原文 →」連結

## 檔案結構

```
gotnews/
├── app.py              # Flask 主應用程式
├── database.py         # SQLite 資料庫操作
├── news_fetcher.py     # NewsAPI 資料抓取
├── requirements.txt    # Python 依賴套件
├── templates/
│   └── index.html     # 前端介面
└── news.db            # SQLite 資料庫檔案（自動建立）
```

## 技術規格

- **後端**：Python Flask
- **資料庫**：SQLite
- **前端**：原生 HTML/CSS/JavaScript
- **API**：NewsAPI v2
- **響應式設計**：支援桌面與行動裝置