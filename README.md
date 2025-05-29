# 🤖 Research Assistant Agent (LLM + VectorDB)

這是一個通用型研究助理系統，透過 GPT 與語意嵌入技術，協助你整合文獻知識與實驗資料，自動回答研究問題與提供建議。

---

## 📁 專案結構

```
research_agent/
├── agent.py                     # 主互動程式：依據語意段落與實驗紀錄回應問題
├── summarize_and_embed.py      # 建立向量資料庫：解析 PDF / Word 並嵌入
├── .env                        # 儲存你的 OpenAI API KEY（請勿上傳）
├── ../experiment_data/
│   ├── papers/                 # 放置 PDF 或 Word 論文全文
│   ├── vector_index/          # 嵌入結果的向量資料庫
│   └── itri_experiment/       # 放入所有實驗紀錄 CSV 檔案
```

---

## ✨ 功能亮點

- ✅ 多檔文獻（PDF / Word）自動語意摘要與嵌入
- ✅ 多檔 CSV 實驗紀錄自動整合
- ✅ 問答回應基於真實資料，不憑空想像
- ✅ 支援條列式建議、自動比對實驗條件
- ✅ 架構可擴充：支援 Notion, SQLite, Streamlit 等整合

---

## 🚀 快速使用

### 1. 安裝依賴套件
```bash
pip install -r requirements.txt
```

### 2. 建立 `.env` 檔案
```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. 建立語意向量資料庫
```bash
python summarize_and_embed.py
```

### 4. 啟動研究助理問答系統
```bash
python agent.py
```

---

## 🔧 可擴充建議

- 自動摘要儀器操作 SOP、專利、報告
- 串接 Notion 或 Google Drive 自動分析內容
- 啟用 GUI（Streamlit、Gradio）提供研究者操作介面