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
7. **Semantic Embedding**: Embedding pipeline supports academic-specific `nomic-ai/nomic-embed-text-v1.5`.

---

## 📂 Project Structure

```
AI-research-agent/
├── research_agent/
│   ├── app/
│   │   ├──browser.py                    # Streamlit file selector
│   │   ├──chunk_embedding.py           # Embedding from PDF metadata
│   │   ├── config.py                    # API keys and path config
│   │   ├──document_renamer.py         # Auto rename and copy uploaded files
│   │   ├──file_upload.py              # Upload handler and pipeline
│   │   ├──knowledge_agent.py          # Core logic for RAG-based QA
│   │   ├──main.py                     # CLI or GUI entry point
│   │   ├──metadata_extractor.py       # Extract DOI, title from PDF/docx
│   │   ├──metadata_registry.py        # Append to experiment log/registry
│   │   ├──pdf_read_and_chunk_page_get.py # Read PDF and locate page number
│   │   ├──perplexity_search_fallback.py # Fallback to Perplexity search
│   │   ├──rag_core.py                 # Load, retrieve, build prompt, call LLM
│   │   ├──research_gui.py             # GUI layout and tab integration
│   │   ├── semantic_lookup.py          # DOI/title query via API
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
✅ Supported Python Versions: 3.10, 3.11
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


🔍 Upcoming: Search Agent for Open Access Chemistry & Materials Data

We are developing a search agent that can:

Interpret user queries and convert them to structured keyword searches

Search open-access scientific databases (e.g. ChemRxiv, EuropePMC, PubChem)

Download PDF or structured data, embed and store it locally

Answer the question using freshly retrieved information

Initially designed for Tab 2 of the GUI, and later will integrate with fallback mode in Tab 1.

---

Maintained by: **this is a self project used in research of ITRI, Taiwan**