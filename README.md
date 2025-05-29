# 🧪 AI Research Assistant

這是一套模組化的 AI 研究助理系統，具備以下核心功能：

## ✅ 功能簡介

1. **知識庫助理**：透過向量資料庫（Chroma）讀取 PDF / Word 文獻與實驗紀錄，並用 GPT 模型回答使用者問題
2. **文獻搜尋**：整合 Perplexity API 即時搜尋有來源的學術資料
3. **互動介面**：使用 Streamlit 建立簡潔易用的網頁介面
4. **CLI 模式**：支援純文字終端互動查詢

---

## 📂 專案結構

```
research_agent/
├── app/
│   ├── main.py                  # 主入口，啟動 GUI 或 CLI
│   ├── config.py                # API 金鑰與路徑設定
│   ├── research_gui.py          # Streamlit 視覺介面
│   ├── knowledge_agent.py       # 向量查詢與回應邏輯
│   ├── perplexity_search_fallback.py  # Perplexity API 呼叫模組
├── experiment_data/
│   ├── vector_index/            # 向量資料庫
│   └── itri_experiment/         # 實驗 CSV 紀錄
├── requirements.txt
└── .env.example
```

---

## 🛠️ 安裝方式

```bash
git clone https://github.com/yourname/research_agent.git
cd research_agent
python -m venv venv
venv\Scripts\activate     # 或 source venv/bin/activate (macOS/Linux)
pip install -r requirements.txt
copy .env.example .env      # 或手動填入 API 金鑰
python app/main.py          # 預設啟動 GUI 模式
```

---

## 🧪 使用模式

### 📘 GUI 模式（預設）
```bash
python app/main.py
```

### 🧠 CLI 模式
```bash
python app/main.py --mode cli
```

---

## 🔑 環境變數設定（.env）

請建立 `.env` 檔案並填入以下內容：

```
OPENAI_API_KEY=your-openai-key
PERPLEXITY_API_KEY=your-perplexity-key
```

---

## 💡 注意事項

- 向量資料庫與實驗記錄路徑由 `config.py` 相對定位，不需手動調整
- Perplexity API 須為 Pro 用戶才能取得 Key：https://www.perplexity.ai/pro