# 🧪 AI Research Assistant v3.1 - Model Selector Edition

A comprehensive AI-powered research assistant system designed for materials science and chemistry research workflows. **Major Update: Enhanced with Model Selector System, Latest Responses API + JSON Schema, and Literature Search Recovery.**

This tool combines document ingestion, vector embedding, GPT-based QA with source tracking, experimental data analysis, and advanced model selection capabilities.

---

## ✨ Key Features

### 🎯 **Proposal Generator** *(Enhanced with JSON Schema)*
- **AI-Powered Research Proposals**: Generate comprehensive research proposals based on your research goals
- **Structured Output**: Uses latest Responses API + JSON Schema for consistent, reproducible proposal formats
- **Chemical Safety Integration**: Automatic chemical information retrieval from PubChem with safety data
- **Interactive Refinement**: Revise proposals based on your feedback and requirements
- **Experiment Detail Generation**: Expand proposals into detailed experimental plans
- **Document Export**: Download complete proposals as Word documents with chemical tables and safety icons
- **Citation Tracking**: Every proposal includes numbered references linking to source documents
- **Smart Text Cleaning**: Automatic markdown format removal for clean document output

### 🤖 **Model Selector System** *(NEW - v1.0)*
- **Multi-Model Support**: Choose from GPT-5, GPT-5 Nano, GPT-5 Mini with real-time switching
- **Dynamic Parameter Configuration**: Adjust max_tokens, timeout, reasoning_effort, verbosity
- **Parameter Validation**: Automatic validation of model-specific parameters and constraints
- **Settings Persistence**: Model preferences and parameters are saved and restored automatically
- **GPT-5 Advanced Features**: Support for reasoning_effort and verbosity controls for enhanced reasoning
- **Bridge Architecture**: Seamless integration between app and backend model configurations

### 🔍 **Literature Search** *(Recovered)*
- **Academic Search Integration**: Real-time academic source retrieval with proper citations
- **Reference Management**: Automatic citation formatting and source tracking
- **Improved Metadata Extracting system**:with higher catching rate, and de-duplication workflow
- **Search History**: Track and manage your search queries (Coming Soon)
- **Europe PMC**: Direct access to biomedical literature (Coming Soon)
- **Perplexity API**: Enhanced search capabilities with academic focus (pending)

### 🖥️ **Enhanced User Interface** *(Updated)*
- **React Frontend**: Modern, responsive web interface built with React 18 + Ant Design
- **FastAPI Backend**: RESTful API architecture for better performance and scalability
- **Real-time Updates**: Live status updates and progress indicators
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Component-based Architecture**: Modular design for easy maintenance and extension
- **Improved Navigation**: Enhanced sidebar and page transitions

### 📥 **Document Embedding & Knowledge Base**
- **Document Processing**: Supports PDF and Word documents with intelligent chunking and metadata extraction
- **Vector Database**: Uses ChromaDB for efficient semantic search and retrieval
- **Academic Embeddings**: Utilizes `nomic-ai/nomic-embed-text-v1.5` for domain-specific semantic understanding
- **Batch Processing**: Upload multiple documents for comprehensive knowledge base building

### 🧪 **Experimental Reasoning Mode** *(Coming Soon)*
- **Dual Retriever Architecture**: Combines literature data with experimental logs for comprehensive analysis
- **Excel Integration**: Processes experimental data from `.xlsx` files and converts to searchable text
- **Synthesis Suggestions**: Provides creative and practical synthesis recommendations based on both literature and experimental data
- **Chemical Safety**: Integrates PubChem data for chemical safety information and NFPA hazard codes

---

## 🎛️ Model Configuration

### Available Models
- **GPT-5**: Latest model with reasoning controls and tool chain support
- **GPT-5 Nano**: Lightweight version for fast, simple formatting tasks
- **GPT-5 Mini**: Balanced version with speed and functionality

### Model Parameters
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
venv_setup.bat

# Start the application
start_react.bat
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

5. **Launch the application**
   ```bash
   # Option 1: Use the batch file (Windows) - Recommended
   start_react.bat
   
   # Option 2: Start services separately
   # Backend
   cd backend && run_api.bat
   # Frontend (in new terminal)
   cd frontend && run_frontend.bat
   ```

The application will open in your default browser at `http://localhost:3000` (React version) or `http://localhost:8000` (Backend API)

---

## 🔑 Environment Configuration

Create a `.env` file in the project root directory:

```env
# Required API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
PERPLEXITY_API_KEY (optional)=pplx-your-perplexity-api-key-here

# Optional: Custom model configurations
# LLM_MODEL_NAME=gpt-5-mini
# EMBEDDING_MODEL_NAME=nomic-ai/nomic-embed-text-v1.5
```

### API Key Setup

After running `venv_setup.bat` or manual installation, you need to configure your API keys:

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

### 📋 **Proposal Generator** (Main Feature - Enhanced)

The Proposal Generator is the primary feature with enhanced structured output:

1. **Enter Research Goal**: Describe your research objective in the text area
2. **Generate Proposal**: Click "✍️ Generate proposal" to create an AI-powered research proposal
3. **Review Results**: The system will display:
   - Complete research proposal (with structured JSON Schema output)
   - Chemical information table with safety data and icons
   - Citations from knowledge base
4. **Refine Proposal**: 
   - Provide feedback and click "💡 Generate New Idea" to revise
   - Click "✅ Accept & Generate Experiment Detail" to expand into detailed experimental plans
5. **Export Document**: Click "📥 Download DOCX" to download the complete proposal as a Word document

**Enhanced Features:**
- **Structured Output**: Uses latest Responses API + JSON Schema for consistent formatting
- **High Reproducibility**: Fixed proposal format ensures consistent results
- **Model Selection**: Choose from GPT-5, GPT-5 Nano, or GPT-5 Mini
- **Parameter Control**: Adjust model parameters for optimal results

### 🔍 **Literature Search** (Recovered)

Access academic literature and research papers:

1. **Search Interface**: Use the Search page to query academic databases
2. **Multiple Sources**: Search across Europe PMC, Perplexity, and other academic sources
3. **Citation Management**: Automatic citation formatting and reference tracking
4. **Integration**: Search results can be used in proposal generation

### ⚙️ **Settings & Model Configuration**

Configure your AI models and parameters:

1. **Model Selection**: Choose your preferred GPT model
2. **Parameter Tuning**: Adjust max_tokens, timeout, and GPT-5-specific parameters
3. **Settings Persistence**: Your preferences are automatically saved
4. **Real-time Updates**: Changes take effect immediately

### 📥 **Document Upload** (Coming Soon)

Upload and process research documents to build your knowledge base:

1. **Upload Documents**: Drag and drop PDF or Word files
2. **Processing**: The system will chunk, embed, and store documents
3. **Knowledge Base**: Documents become searchable for proposal generation

---

## 🏗️ Architecture

### React Version (Current)
```
frontend/                 # React 18 + Vite + Ant Design
├── src/
│   ├── pages/           # Page components (Proposal, Search, Settings, etc.)
│   ├── components/      # Reusable components
│   └── services/        # API services
backend/                  # FastAPI backend
├── api/routes/          # API endpoints
│   ├── proposal.py      # Proposal generation
│   ├── search.py        # Literature search
│   ├── settings.py      # Model configuration
│   └── knowledge.py     # Knowledge queries
├── core/                # Core configuration
│   ├── settings_manager.py  # Model and parameter management
│   └── config.py        # Application configuration
└── main.py              # FastAPI application
app/                     # Legacy Streamlit components
├── model_config_bridge.py  # Bridge between app and backend
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

4. **Model configuration issues**
   - Check Settings page for model availability
   - Verify API key has access to selected model
   - Reset settings if parameters are invalid

---

## 🚧 Future Work

### 🔍 **Enhanced Retrieval System**
- **Improved Article Retrieval**: Enhance retriever capabilities for better answer relevance
- **Advanced Search Algorithms**: Implement more sophisticated search and ranking methods
- **Multi-modal Retrieval**: Support for images, tables, and other document elements

### 🤖 **Local LLM Integration**
- **OSS-20B Local Model**: Update and integrate OSS-20B for local LLM running
- **Offline Capabilities**: Enable full offline operation with local models

### 🎯 **Interactive Features**
- **Text Highlighting**: Select text for LLM explanation and modification
- **Proposal Mode Integration**: Direct text editing and modification in proposal mode
- **Real-time Collaboration**: Multi-user editing and commenting features

### 💬 **Conversation Management**
- **History Tracking**: Maintain conversation history across sessions
- **Context Preservation**: Keep context for long research sessions
- **Export Conversations**: Save and share research conversations
- **Proposal-based project switch**: manage undergoing projects with all the past info saved

### 🧪 **Research Advisor**
- **Data Reception**: Accept and process experimental data
- **Data Visualization**: Display experimental results and trends
- **AI-Assisted Analysis**: Provide insights and suggestions based on data
- **Experimental Recommendations**: Suggest next steps and improvements

### 📊 **Dashboard Features**
- **Research Progress Tracking**: Monitor proposal and experiment progress
- **Analytics Dashboard**: Visualize research metrics and trends
- **Project Management**: Organize and track multiple research projects
- **API Key setting function**: Import API key from setting page


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
- **ITRI AI team** 宗霖、偉倫、素結 for brainstorming and suggestions

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/z8z0028z4/AI-research-agent/issues)
- **Documentation**: See `app/ARCHITECTURE_OVERVIEW.md`
- **Learning Guide**: See `app/LEARNING_GUIDE.md`
- **Usage Guide**: See `USAGE_GUIDE.md`

---

*Last updated: 15, Augest, 2025 - Model Selector Edition v3.1*
