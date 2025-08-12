# 🧪 AI Research Assistant v3.0 - React Edition

A comprehensive AI-powered research assistant system designed for materials science and chemistry research workflows. **Major Update: Migrated from Streamlit to React frontend for better user experience and modern UI.**

This tool combines document ingestion, vector embedding, GPT-based QA with source tracking, and experimental data analysis capabilities.

---

## ✨ Key Features

### 🎯 **Proposal Generator** *(React Version - Enhanced)*
- **AI-Powered Research Proposals**: Generate comprehensive research proposals based on your research goals
- **Chemical Safety Integration**: Automatic chemical information retrieval from PubChem with safety data
- **Interactive Refinement**: Revise proposals based on your feedback and requirements
- **Experiment Detail Generation**: Expand proposals into detailed experimental plans
- **Document Export**: Download complete proposals as Word documents with chemical tables and safety icons
- **Citation Tracking**: Every proposal includes numbered references linking to source documents
- **Smart Text Cleaning**: Automatic markdown format removal for clean document output

### 🤖 **Model Selector** *(NEW - Model Selection System)*
- **Multi-Model Support**: Choose from GPT-5, GPT-5 Nano, GPT-5 Mini, and GPT-4 Turbo Preview
- **Dynamic Parameter Configuration**: Adjust temperature, max tokens, timeout, and GPT-5-specific parameters
- **Real-time Model Switching**: Change models on-the-fly without restarting the application
- **Parameter Validation**: Automatic validation of model-specific parameters and constraints
- **Settings Persistence**: Model preferences and parameters are saved and restored automatically
- **GPT-5 Advanced Features**: Support for reasoning_effort and verbosity controls for enhanced reasoning

### 🖥️ **Modern User Interface** *(NEW)*
- **React Frontend**: Modern, responsive web interface built with React 18 + Ant Design
- **FastAPI Backend**: RESTful API architecture for better performance and scalability
- **Real-time Updates**: Live status updates and progress indicators
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Component-based Architecture**: Modular design for easy maintenance and extension

### 📥 **Document Embedding & Knowledge Base**
- **Document Processing**: Supports PDF and Word documents with intelligent chunking and metadata extraction
- **Vector Database**: Uses ChromaDB for efficient semantic search and retrieval
- **Academic Embeddings**: Utilizes `nomic-ai/nomic-embed-text-v1.5` for domain-specific semantic understanding
- **Batch Processing**: Upload multiple documents for comprehensive knowledge base building

### 🔍 **Knowledge Assistant** *(Coming Soon)*
- **Citation Tracking**: Every response includes numbered references `[1]` linking to source documents, pages, and text snippets
- **Multiple Answer Modes**: Choose between strict citation mode, extended reasoning, or experimental data integration

### 🧪 **Experimental Reasoning Mode** *(Coming Soon)*
- **Dual Retriever Architecture**: Combines literature data with experimental logs for comprehensive analysis
- **Excel Integration**: Processes experimental data from `.xlsx` files and converts to searchable text
- **Synthesis Suggestions**: Provides creative and practical synthesis recommendations based on both literature and experimental data
- **Chemical Safety**: Integrates PubChem data for chemical safety information and NFPA hazard codes

### 🔬 **Academic Search Integration** *(Coming Soon)*
- **Perplexity API**: Real-time academic source retrieval with proper citations
- **Europe PMC**: Direct access to biomedical literature
- **Reference Management**: Automatic citation formatting and source tracking

---

## 🎛️ Model Configuration

### Available Models
- **GPT-5**: Latest model with reasoning controls and tool chain support
- **GPT-5 Nano**: Lightweight version for fast, simple formatting tasks
- **GPT-5 Mini**: Balanced version with speed and functionality
- **GPT-4 Turbo Preview**: Stable, reliable model with traditional API interface

### Model Parameters
- **Temperature**: Controls response randomness (0.0-2.0)
- **Max Tokens**: Maximum response length (1-32,000)
- **Timeout**: Request timeout in seconds (10-600)
- **Reasoning Effort** (GPT-5 only): Controls reasoning depth (minimal/low/medium/high)
- **Verbosity** (GPT-5 only): Controls response detail level (low/medium/high)

### Configuration
Access the Settings page in the React interface to:
1. Select your preferred model
2. Adjust model parameters
3. Save settings for future sessions
4. View model-specific parameter information

---

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.10 or 3.11 or 3.12
- **Node.js**: 16.0 or higher
- **Memory**: Minimum 8GB RAM (16GB recommended for large document sets)
- **Storage**: At least 2GB free space for vector database

### Installation

**Option 1: Quick Installation (Windows) - Recommended**
```bash
# Run the automated installation script
install.bat

# Start the React application
start_react_app.bat
```

**Option 2: Manual Installation**

1. **Clone the repository**
   ```bash
   git clone https://github.com/z8z0028z4/AI-research-agent.git
   cd AI-research-agent
   ```

2. **Install Python dependencies**
   ```bash
   # Create virtual environment
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   # macOS/Linux
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   ```

3. **Install Node.js dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your_api_key_here
   ```
   cp env.example research_agent/.env
   # Edit research_agent/.env file with your API keys
   ```

5. **Launch the application**
   ```bash
   # Option 1: Use the batch file (Windows) - Recommended
   start_react_app.bat
   
   # Option 2: Start services separately
   # Backend
   cd backend && run_api.bat
   # Frontend (in new terminal)
   cd frontend && run_frontend.bat
   
   # Option 3: Legacy Streamlit version
   run.bat
   ```

The application will open in your default browser at `http://localhost:3000` (React version) or `http://localhost:8501` (Streamlit version)

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

After running `install.bat` or manual installation, you need to configure your API keys:

1. **Edit the `.env` file** in the `research_agent/` directory
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

### 📋 **Proposal Generator** (Main Feature - React Version)

The Proposal Generator is the primary feature of this release. Here's how to use it:

1. **Enter Research Goal**: Describe your research objective in the text area
2. **Generate Proposal**: Click "✍️ Generate proposal" to create an AI-powered research proposal
3. **Review Results**: The system will display:
   - Complete research proposal (with smart text cleaning)
   - Chemical information table with safety data and icons
   - Citations from knowledge base
4. **Refine Proposal**: 
   - Provide feedback and click "💡 Generate New Idea" to revise
   - Click "✅ Accept & Generate Experiment Detail" to expand into detailed experimental plans
5. **Export Document**: Click "📥 Download DOCX" to download the complete proposal as a Word document

**Enhanced Features:**
- Modern React UI with responsive design
- Automatic chemical safety data retrieval from PubChem
- Interactive proposal refinement based on user feedback
- Detailed experimental plan generation
- Professional document export with chemical tables and safety icons
- Smart text cleaning (removes markdown formatting)

### 📥 **Document Embedding** (Coming Soon)

Upload and process research documents to build your knowledge base:

1. **Upload Documents**: Drag and drop PDF or Word files
2. **Processing**: The system will chunk, embed, and store documents
3. **Knowledge Base**: Documents become searchable for proposal generation

### 🔧 **Enabling Other Features**

Currently, only the Proposal Generator feature is fully implemented in the React version. Other features are being migrated:

**React Version (Current):**
- ✅ Proposal Generator
- ✅ Chemical Information Lookup
- ✅ DOCX Export
- 🔄 Document Upload (In Progress)
- 🔄 Literature Search (Coming Soon)
- 🔄 Knowledge Assistant (Coming Soon)

**Legacy Streamlit Version:**
- ✅ All features available
- Use `run.bat` to start the Streamlit version

---

## 🏗️ Architecture

### React Version (New)
```
frontend/                 # React 18 + Vite + Ant Design
├── src/
│   ├── pages/           # Page components
│   ├── components/      # Reusable components
│   └── services/        # API services
backend/                  # FastAPI backend
├── api/routes/          # API endpoints
├── core/                # Core configuration
└── main.py              # FastAPI application
```

### Legacy Streamlit Version
```
app/                     # Streamlit application
├── main.py              # Main application
├── knowledge_agent.py   # AI agent logic
└── rag_core.py          # RAG implementation
```

---

## 🛠️ Troubleshooting

### React Version Issues

1. **Frontend not starting**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

2. **Backend API errors**
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

3. **Port conflicts**
   - Frontend: http://localhost:3000
   - Backend: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

### Common Issues

1. **"Module not found" errors**
   ```bash
   pip install -r requirements.txt --upgrade
   pip install -r backend/requirements.txt --upgrade
   ```

2. **Node.js version issues**
   ```bash
   node --version  # Should be >= 16.0
   npm --version
   ```

3. **API connection errors**
   - Check if backend is running on port 8000
   - Check browser console for CORS errors
   - Verify API keys in `.env` file

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Backend development
cd backend
pip install -r requirements.txt
python main.py

# Frontend development
cd frontend
npm install
npm run dev
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT models and API
- **Perplexity** for academic search capabilities
- **ChromaDB** for vector database functionality
- **React** and **Ant Design** for the modern UI framework
- **FastAPI** for the backend API framework
- **PubChem** for chemical safety data
- **Europe PMC** for biomedical literature access

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/z8z0028z4/AI-research-agent/issues)
- **Documentation**: See `app/ARCHITECTURE_OVERVIEW.md`
- **React Guide**: See `README_REACT.md`
- **Learning Guide**: See `app/LEARNING_GUIDE.md`

---

*Last updated: January 2025 - React Version v3.0*