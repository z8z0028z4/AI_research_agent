# 🧪 AI Research Assistant v2.0

A comprehensive AI-powered research assistant system designed for materials science and chemistry research workflows. This tool combines document ingestion, vector embedding, GPT-based QA with source tracking, and experimental data analysis capabilities.

---

## ✨ Key Features

### 🎯 **Proposal Generator** *(NEW - Main Feature)*
- **AI-Powered Research Proposals**: Generate comprehensive research proposals based on your research goals
- **Chemical Safety Integration**: Automatic chemical information retrieval from PubChem with safety data
- **Interactive Refinement**: Revise proposals based on your feedback and requirements
- **Experiment Detail Generation**: Expand proposals into detailed experimental plans
- **Document Export**: Download complete proposals as Word documents with chemical tables and safety icons
- **Citation Tracking**: Every proposal includes numbered references linking to source documents

### 📥 **Document Embedding & Knowledge Base**
- **Document Processing**: Supports PDF and Word documents with intelligent chunking and metadata extraction
- **Vector Database**: Uses ChromaDB for efficient semantic search and retrieval
- **Academic Embeddings**: Utilizes `nomic-ai/nomic-embed-text-v1.5` for domain-specific semantic understanding
- **Batch Processing**: Upload multiple documents for comprehensive knowledge base building

### 🔍 **Knowledge Assistant** *(Currently Disabled)*
- **Citation Tracking**: Every response includes numbered references `[1]` linking to source documents, pages, and text snippets
- **Multiple Answer Modes**: Choose between strict citation mode, extended reasoning, or experimental data integration

### 🧪 **Experimental Reasoning Mode** *(Currently Disabled)*
- **Dual Retriever Architecture**: Combines literature data with experimental logs for comprehensive analysis
- **Excel Integration**: Processes experimental data from `.xlsx` files and converts to searchable text
- **Synthesis Suggestions**: Provides creative and practical synthesis recommendations based on both literature and experimental data
- **Chemical Safety**: Integrates PubChem data for chemical safety information and NFPA hazard codes

### 🔬 **Academic Search Integration** *(Currently Disabled)*
- **Perplexity API**: Real-time academic source retrieval with proper citations
- **Europe PMC**: Direct access to biomedical literature
- **Reference Management**: Automatic citation formatting and source tracking

### 🖥️ **User Interface**
- **Streamlit GUI**: Clean, modern web interface with tabbed navigation
- **CLI Mode**: Command-line interface for minimal setups and automation
- **File Upload**: Drag-and-drop support for documents and experimental data
- **Real-time Processing**: Live status updates and progress indicators

---

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.10 or 3.11 or 3.12
- **Memory**: Minimum 8GB RAM (16GB recommended for large document sets)
- **Storage**: At least 2GB free space for vector database

### Installation

**Option 1: Quick Installation (Windows)**
```bash
# Run the automated installation script
install.bat
```

**Option 2: Manual Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/z8z0028z4/AI-research-agent.git
   cd AI-research-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv_company
   # Windows
   venv_company\Scripts\activate
   # macOS/Linux
   source venv_company/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env file with your API keys
   ```

5. **Launch the application**
   ```bash
   # Option 1: Use the batch file (Windows)
   run.bat
   
   # Option 2: Direct Python execution
   python app/main.py
   
   # Option 3: Use the root launcher
   python run_from_root.py
   ```

The application will open in your default browser at `http://localhost:8501`

---

## 🔑 Environment Configuration

Create a `.env` file in the project root directory:

```env
# Required API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
PERPLEXITY_API_KEY (optional)=pplx-your-perplexity-api-key-here

# Optional: Custom model configurations
# LLM_MODEL_NAME=gpt-4-1106-preview
# EMBEDDING_MODEL_NAME=nomic-ai/nomic-embed-text-v1.5
```

### API Key Setup

After running `install.bat` or manual installation, you need to configure your API keys:

1. **Edit the `.env` file** in the project root directory
2. **Add your API keys**:
   - **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
   - **Perplexity API Key**: Get from [Perplexity API](https://www.perplexity.ai/settings/api) (optional)

Example `.env` file:
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
PERPLEXITY_API_KEY=pplx-your-perplexity-api-key-here
```

---

## 🎯 Usage Guide

### 📋 **Proposal Generator** (Main Feature)

The Proposal Generator is the primary feature of this release. Here's how to use it:

1. **Enter Research Goal**: Describe your research objective in the text area
2. **Generate Proposal**: Click "Generate proposal" to create an AI-powered research proposal
3. **Review Results**: The system will display:
   - Complete research proposal
   - Chemical information table with safety data
   - Citations from knowledge base
4. **Refine Proposal**: 
   - Provide feedback and click "Generate New Idea" to revise
   - Click "Accept & Generate Experiment Detail" to expand into detailed experimental plans
5. **Export Document**: Download the complete proposal as a Word document

**Features:**
- Automatic chemical safety data retrieval from PubChem
- Interactive proposal refinement based on user feedback
- Detailed experimental plan generation
- Professional document export with chemical tables and safety icons

### 📥 **Document Embedding**

Upload and process research documents to build your knowledge base:

1. **Upload Documents**: Drag and drop PDF or Word files
2. **Processing**: The system will chunk, embed, and store documents
3. **Knowledge Base**: Documents become searchable for proposal generation

### 🔧 **Enabling Other Features**

Currently, only the Proposal Generator and Document Embedding features are enabled. To enable other features:

1. **Edit `app/research_gui.py`**
2. **Modify the `TAB_FLAGS` dictionary**:
   ```python
   TAB_FLAGS = {
       "tab_1_proposal_generator": True,    # Currently enabled
       "tab_2_embedding": True,             # Currently enabled
       "tab_3_search_pdf": False,           # Set to True to enable
       "tab_4_perplexity_search": False,    # Set to True to enable
       "tab_5_research_assitant": False     # Set to True to enable
   }
   ```

**Available Features to Enable:**
- **Search PDF**: External literature search and PDF download
- **Perplexity Search**: Real-time academic search using Perplexity API
- **Knowledge Assistant**: Q&A with knowledge base using different reasoning modes

---

## 📚 Supported File Formats

### Input Documents
- **PDF**: Research papers, reports, manuals
- **DOCX**: Word documents, reports
- **XLSX**: Experimental data, measurement logs
- **TXT**: Plain text files

### Output Formats
- **DOCX**: Generated proposals with chemical safety data
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
   pip install -r requirements.txt --upgrade
   ```

2. **Streamlit startup issues**
   ```bash
   # Use the modified startup command
   python app/main.py
   ```

3. **SSL Certificate errors**
   - The system automatically handles SSL issues
   - Check your corporate firewall settings

4. **Memory issues with large documents**
   - Reduce document chunk size in `config.py`
   - Process documents in smaller batches

5. **API rate limiting**
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
pip install -r requirements.txt
pip install pytest black flake8

# Run tests
pytest app/

# Code formatting
black app/
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
- **Documentation**: See `app/ARCHITECTURE_OVERVIEW.md`
- **Learning Guide**: See `app/LEARNING_GUIDE.md`

---

*Last updated: January 2025*
