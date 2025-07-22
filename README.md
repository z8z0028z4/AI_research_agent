# 🧪 AI Research Assistant

A modular AI assistant system designed for research workflows, particularly in materials science and chemistry. This tool supports document ingestion, vector embedding, and GPT-based QA with source tracking.

---

## ✅ Features

1. **Knowledge Assistant**: Leverages Chroma vector database to embed and retrieve content from PDF/Word documents and experimental records. GPT answers user questions with citation traceability.
2. **Experimental Reasoning Mode (NEW)**: Dual Retriever architecture—allows the assistant to reason with both **literature data** and **user-uploaded experimental logs**, providing creative and practical synthesis suggestions.
3. **Academic Search**: Integrates Perplexity API for real-time academic source retrieval with references.
4. **Interactive GUI**: Built with Streamlit for a clean and simple web interface.
5. **CLI Mode**: Supports command-line interaction for minimal setups.
6. **Document Tracing**: Embedded chunks now include metadata such as filename, tracing number, page number, and paragraph snippet.
7. **Reference Injection**: GPT responses include numbered references `[1]`, linking to document, page, and chunk beginning text for traceability.
8. **Semantic Embedding**: Embedding pipeline supports academic-specific `nomic-ai/nomic-embed-text-v1.5`.

---

## 📂 Project Structure

```
AI-research-agent/
├── research_agent/
│   ├── app/
│   │   ├──browser.py
│   │   ├──chunk_embedding.py
│   │   ├── config.py
│   │   ├──document_renamer.py
│   │   ├──file_upload.py
│   │   ├──knowledge_agent.py
│   │   ├──main.py
│   │   ├──metadata_extractor.py
│   │   ├──metadata_registry.py
│   │   ├──pdf_read_and_chunk_page_get.py
│   │   ├──perplexity_search_fallback.py
│   │   ├──rag_core.py
│   │   ├──research_gui.py
│   │   ├──semantic_lookup.py
│   │   ├──verify_embedding.py
│   ├── requirements.txt
│   ├── run.bat
│   ├── README.md
│   └── .env.example
└── experiment_data/
    ├── papers/
    ├── vector_index/
    └── experiment/
```

---

## 🧠 Modes of Use

### 📘 GUI Mode (default)
```bash
python app/main.py
```

### 🧠 CLI Mode
```bash
python app/main.py --mode cli
```

### 🧪 Experimental Reasoning Mode
- Access via GUI Tab 1 → 選擇模式：「納入實驗資料，進行推論與建議」
- Embeds `.xlsx` experimental logs and retrieves them alongside literature for dual-context prompting.

---

## 🛠️ Installation

```bash
git clone https://github.com/yourname/research_agent.git
cd research_agent
python -m venv venv
venv\Scripts\activate      # or source venv/bin/activate (macOS/Linux)
pip install -r requirements.txt
cp .env.example .env         # or fill in keys manually
python app/main.py           # GUI mode by default
✅ Supported Python Versions: 3.10, 3.11
```

---

## 🔑 Environment Variables (`.env`)

```
OPENAI_API_KEY=your-openai-key
PERPLEXITY_API_KEY=your-perplexity-key
```

---

## 🔍 Notes

- All path configurations (papers, vectors) are relative, managed via `config.py`
- `vector_index/` 資料夾下有兩種 Collection:
  - `paper`：來自文獻的 embedding
  - `experiment`：由 Excel 匯出 `.txt` 的實驗資料
- Dual Retriever 啟用時，語意查詢將拓展後檢索文獻資料，並使用原始語句查詢實驗向量資料