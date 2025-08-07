# 🧪 AI Research Assistant v2.0

A comprehensive AI-powered research assistant system designed for materials science and chemistry research workflows. This tool combines document ingestion, vector embedding, GPT-based QA with source tracking, and experimental data analysis capabilities.

---

## ✨ Key Features

### 🔍 **Knowledge Assistant**
- **Document Processing**: Supports PDF and Word documents with intelligent chunking and metadata extraction
- **Vector Database**: Uses ChromaDB for efficient semantic search and retrieval
- **Citation Tracking**: Every response includes numbered references `[1]` linking to source documents, pages, and text snippets
- **Academic Embeddings**: Utilizes `nomic-ai/nomic-embed-text-v1.5` for domain-specific semantic understanding

### 🧪 **Experimental Reasoning Mode** *(NEW)*
- **Dual Retriever Architecture**: Combines literature data with experimental logs for comprehensive analysis
- **Excel Integration**: Processes experimental data from `.xlsx` files and converts to searchable text
- **Synthesis Suggestions**: Provides creative and practical synthesis recommendations based on both literature and experimental data
- **Chemical Safety**: Integrates PubChem data for chemical safety information and NFPA hazard codes

### 🔬 **Academic Search Integration**
- **Perplexity API**: Real-time academic source retrieval with proper citations
- **Europe PMC**: Direct access to biomedical literature
- **Reference Management**: Automatic citation formatting and source tracking

### 🖥️ **User Interface**
- **Streamlit GUI**: Clean, modern web interface with tabbed navigation
- **CLI Mode**: Command-line interface for minimal setups and automation
- **File Upload**: Drag-and-drop support for documents and experimental data
- **Real-time Processing**: Live status updates and progress indicators

---

## 📂 Project Structure

```
AI-research-agent/
├── research_agent/
│   ├── app/
│   │   ├── main.py                 # Application entry point
│   │   ├── research_gui.py         # Streamlit GUI interface
│   │   ├── config.py               # Configuration management
│   │   ├── rag_core.py             # RAG (Retrieval-Augmented Generation) core
│   │   ├── knowledge_agent.py      # Knowledge processing agent
│   │   ├── chunk_embedding.py      # Document chunking and embedding
│   │   ├── browser.py              # File browser and selection
│   │   ├── file_upload.py          # File upload processing
│   │   ├── perplexity_search_fallback.py  # Academic search integration
│   │   ├── pubchem_handler.py      # Chemical data integration
│   │   ├── europepmc_handler.py    # Europe PMC integration
│   │   ├── search_agent.py         # Search functionality
│   │   ├── query_parser.py         # Query parsing and processing
│   │   ├── metadata_extractor.py   # Document metadata extraction
│   │   ├── metadata_registry.py    # Metadata management
│   │   └── excel_to_txt_by_row.py  # Excel to text conversion
│   ├── requirements.txt            # Python dependencies
│   ├── env.example                 # Environment variables template
│   ├── run.bat                     # Windows startup script
│   └── README.md                   # This file
├── experiment_data/
│   ├── papers/                     # Research papers and documents
│   ├── experiment/                 # Experimental data files
│   ├── vector_index/               # Vector database storage
│   └── metadata_registry.xlsx      # Document metadata registry
└── conductive mof/                 # Domain-specific research materials
```

---

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.10 or 3.11
- **Memory**: Minimum 8GB RAM (16GB recommended for large document sets)
- **Storage**: At least 2GB free space for vector database

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/z8z0028z4/AI-research-agent.git
   cd AI-research-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r research_agent/requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp research_agent/env.example research_agent/.env
   # Edit .env file with your API keys
   ```

5. **Launch the application**
   ```bash
   cd research_agent
   python app/main.py
   ```

The application will open in your default browser at `http://localhost:8501`

---

## 🔑 Environment Configuration

Create a `.env` file in the `research_agent/` directory:

```env
# Required API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
PERPLEXITY_API_KEY (optional)=pplx-your-perplexity-api-key-here

# Optional: Custom model configurations
# LLM_MODEL_NAME=gpt-4-1106-preview
# EMBEDDING_MODEL_NAME=nomic-ai/nomic-embed-text-v1.5
```

### API Key Setup

1. **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
2. **Perplexity API Key**: Get from [Perplexity API](https://www.perplexity.ai/settings/api)

---

## 🎯 Usage Modes

### 📘 GUI Mode (Default)
```bash
python app/main.py
```
- **Tab 1**: Proposal mode - drafting your research proposal
- **Tab 2**: Literature embedding 

### 🖥️ CLI Mode
```bash
python app/main.py --mode cli
```
*Note: CLI mode is under development*

### 🧪 Experimental Reasoning Mode
1. Upload experimental data (`.xlsx` files) in Tab 3
2. Select "納入實驗資料，進行推論與建議" mode
3. Ask synthesis or experimental questions
4. Get responses based on both literature and experimental data

---

## 📚 Supported File Formats

### Input Documents
- **PDF**: Research papers, reports, manuals
- **DOCX**: Word documents, reports
- **XLSX**: Experimental data, measurement logs
- **TXT**: Plain text files

### Output Formats
- **DOCX**: Generated reports with chemical safety data
- **PNG**: Chemical hazard icons and safety diagrams
- **JSON**: Structured chemical data from PubChem

---

## 🔧 Advanced Configuration

### Custom Model Settings
Edit `app/config.py` to customize:
- Embedding model selection
- LLM parameters (temperature, max tokens)
- Vector database settings
- File path configurations

### Vector Database Management
- **Location**: `experiment_data/vector_index/`
- **Collections**: 
  - `paper`: Literature embeddings
  - `experiment`: Experimental data embeddings
- **Backup**: ChromaDB automatically handles persistence

### SSL Certificate Issues
The system includes automatic SSL certificate handling for enterprise environments. If you encounter SSL issues, the system will automatically bypass certificate verification.

---

## 🛠️ Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r research_agent/requirements.txt --upgrade
   ```

2. **SSL Certificate errors**
   - The system automatically handles SSL issues
   - Check your corporate firewall settings

3. **Memory issues with large documents**
   - Reduce document chunk size in `config.py`
   - Process documents in smaller batches

4. **API rate limiting**
   - Check your OpenAI and Perplexity API quotas
   - Implement rate limiting in your queries

### Performance Optimization

- **Memory optimization**: Process documents in batches
- **Speed optimization**: Use smaller embedding models for faster processing

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r research_agent/requirements.txt
pip install pytest black flake8

# Run tests
pytest research_agent/app/

# Code formatting
black research_agent/app/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT models and API
- **Perplexity** for academic search capabilities
- **ChromaDB** for vector database functionality
- **Streamlit** for the web interface framework
- **PubChem** for chemical safety data
- **Europe PMC** for biomedical literature access

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/z8z0028z4/AI-research-agent/issues)
- **Documentation**: See `research_agent/app/ARCHITECTURE_OVERVIEW.md`
- **Learning Guide**: See `research_agent/app/LEARNING_GUIDE.md`

---

*Last updated: January 2025*
