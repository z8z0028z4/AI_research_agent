# 🧪 AI Research Assistant

A modular AI assistant system designed for research workflows, particularly in materials science and chemistry. This tool supports document ingestion, vector embedding, and GPT-based QA with source tracking.

---

## ✅ Features

1. **Knowledge Assistant**: Leverages Chroma vector database to embed and retrieve content from PDF/Word documents and experimental records. GPT answers user questions with citation traceability.
2. **Academic Search**: Integrates Perplexity API for real-time academic source retrieval with references.
3. **Interactive GUI**: Built with Streamlit for a clean and simple web interface.
4. **CLI Mode**: Supports command-line interaction for minimal setups.
5. **Document Tracing**: Embedded chunks now include metadata such as filename, tracing number, page number, and paragraph snippet.
6. **Reference Injection**: GPT responses include numbered references `[1]`, linking to document, page, and chunk beginning text for traceability.
7. **Semantic Embedding**: Embedding pipeline supports switching to academic-specific models such as `Instructor-XL`, `Specter2`, or `SciNCL`.

---

## 📂 Project Structure

```
AI-research-agent/
├── research_agent/
│   ├── app/
│   │   ├── main.py                       # Entry point (GUI/CLI)
│   │   ├── config.py                     # API keys and directory config
│   │   ├── research_gui.py               # Streamlit GUI workflow
│   │   ├── knowledge_agent.py            # Vector-based QA logic
│   │   ├── summarize_and_embed.py        # PDF/docx embedding + tracing
│   │   ├── semantic_lookup.py            # DOI & title metadata query
│   │   ├── perplexity_search_fallback.py # API-based fallback document search
│   │   ├── browser.py                    # Streamlit file selector
│   │   ├── document_renamer.py           # Auto file renaming + tracing number
│   │   ├── file_upload.py                # Unified upload + metadata ingestion
│   │   ├── metadata_extractor.py         # Extract DOI/title/type from text
│   │   ├── metadata_registry.py          # Registry appending (XLSX)
│   ├── requirements.txt
│   ├── run.bat
│   ├── README.md
│   ├── logo.txt
│   └── .env.example
└── experiment_data/
    ├── papers/                     # Named + moved PDF archive
    ├── vector_index/               # Chroma vector DB
    └── experiment/                 # CSV logs of experiments
```

---

## 🛠️ Installation

```bash
git clone https://github.com/yourname/research_agent.git
cd research_agent
python -m venv venv
venv\Scripts\activate      # or source venv/bin/activate (macOS/Linux)
pip install -r requirements.txt
cp .env.example .env       # or fill in keys manually
python app/main.py         # GUI mode by default
```

---

## 🚀 Modes of Use

### 📘 GUI Mode (default)
```bash
python app/main.py
```

### 🧠 CLI Mode
```bash
python app/main.py --mode cli
```

---

## 🔑 Environment Variables (`.env`)

```
OPENAI_API_KEY=your-openai-key
PERPLEXITY_API_KEY=your-perplexity-key
```

---

## 📌 Notes

- All path configurations (papers, vectors) are relative, managed via `config.py`
- Perplexity API requires a Pro account: https://www.perplexity.ai/pro
- Vector chunks include: `filename`, `page_number`, `chunk_index`, `tracing_number`, and snippet of the paragraph for fast lookup.

---

## 🧪 Recommended Embedding Models for Chemistry & Materials

| Model | Strength | HF Path |
|-------|----------|---------|
| `hkunlp/instructor-xl` | Instruction-guided, versatile | ✅ Recommended |
| `allenai/specter2` | Fine-tuned on scientific citations | Suitable |
| `microsoft/SciNCL-Base` | Embedding with contrastive learning | Optional |
| `bge-m3`, `bge-large-en` | Multi-task (retrieval, QA, summarization) | Optional |

> Replace default OpenAI embeddings in `summarize_and_embed.py` if needed.

---

## 🧭 Roadmap

- [x] File selection browser with automatic renaming and metadata tracking
- [x] Automatic vector embedding with citation trace
- [ ] link to large open acess paper database for gathering more useful information 
- [ ] Switch to academic-tuned embedding models
- [ ] interaction between agent and perplexity, searching website when database is not enough
- [ ] Add Notion/Google Drive sync and file watching

---

Maintained by: **this is a self project used in research of ITRI, Taiwan**