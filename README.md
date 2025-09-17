# 🧪 AI Research Assistant v4.6 - GPT-5-nano Integration & TextHighlight Restoration Release

A comprehensive AI-powered research assistant system designed for materials science and chemistry research workflows. **Enhanced Production Release: Complete system with GPT-5-nano integration, TextHighlight functionality, and comprehensive testing framework.**

This production-ready tool combines document ingestion, vector embedding, GPT-based QA with source tracking, experimental data analysis, intelligent content management, and robust configuration management.

---

## 🎉 v4.6 GPT-5-nano Integration & TextHighlight Restoration Release Highlights

This release introduces **GPT-5-nano integration** for cost-effective AI processing, **TextHighlight functionality restoration**, and **comprehensive testing framework** with real API testing capabilities.

### 🆕 **v4.6 New Features**

- **🤖 GPT-5-nano Integration**: Cost-effective AI processing with 97% cost reduction
  - Replaced GPT-4 with GPT-5-nano for metadata extraction and file classification
  - JSON Schema integration ensures consistent output format
  - Maintained high accuracy (100% in testing) with significant cost savings
  - Enhanced error handling and API parameter optimization
- **🔍 TextHighlight Functionality Restoration**: Complete text interaction system
  - Restored text highlighting and popup interaction features
  - Integrated text selection for LLM explanation and modification
  - Cross-page text interaction with context preservation
  - Enhanced user experience for document analysis and editing
- **🧪 Comprehensive Testing Framework**: Complete test suite with real API testing
  - Real API Tests: All tests use actual API calls and real data (no mocks)
  - Text Interaction Tests: Complete testing of text highlighting functionality
  - Proposal E2E Tests: Full end-to-end testing of proposal generation workflows
  - Test Configuration Fixes: Resolved pytest configuration issues
  - Interactive Test Runner: User-friendly test execution with `run_tests.bat`
- **💾 Global State Management**: React Context-based state management system
  - Cross-tab data persistence for all pages (Proposal, Search, KnowledgeQuery)
  - Automatic localStorage backup and restoration
  - Seamless state synchronization across components
- **🔄 UI Persistence**: Enhanced user experience with persistent data
  - Generated proposals remain intact when switching tabs
  - Search results and knowledge queries are preserved
  - Form data and user inputs are automatically saved
  - Page refresh recovery for all generated content
- **📊 State Management Tools**: Comprehensive data management interface
  - Real-time data statistics and monitoring
  - Export/import functionality for data backup
  - Selective data clearing (by page or all data)
  - Visual data status indicators
- **🔧 Embedding Model Upgrade**: Upgraded from `BAAI/bge-small-zh-v1.5` to `BAAI/bge-base-en-v1.5`
  - Enhanced English semantic understanding capabilities
  - Better cross-language retrieval performance
  - CPU-friendly architecture with reduced resource consumption
  - Improved vector retrieval accuracy and relevance
- **🛠️ System Installation Fixes**: Fixed `simple_setup.bat` script issues
  - Improved virtual environment setup process
  - Optimized dependency installation workflow
  - Enhanced installation success rate
- **⚡ Performance Improvements**: Better CPU efficiency and processing speed
- **🧪 SMILES Chemical Structure Integration**: Enhanced chemical structure visualization and DOCX integration
- **🔧 Development Mode**: Configurable chunk retrieval for faster testing and development
- **⚡ CPU/GPU Installation Options**: Smart setup script with CPU vs CUDA version selection
- **🐛 Bug Fixes**: Comprehensive fixes for citation management and proposal revision workflows

---

## ✨ Key Features

### 🎯 **Core Features**

- **AI Proposal Generator**: Create and refine research proposals with automatic chemical safety info and citation tracking
- **Smart Document Management**: Upload, classify, and deduplicate research files (PDF, DOCX) with automatic metadata enrichment
- **Knowledge Base & Embedding**: Build searchable knowledge base using advanced embeddings (CPU-optimized)
- **Chemical Structure Support**: Visualize and insert chemical structures (SMILES) into Word documents
- **TextHighlight Interaction**: Select and interact with text for LLM explanation and modification
- **State Persistence**: Automatic saving and restoration of all generated content across tab switches and page refreshes
- **Cost-Effective AI Processing**: GPT-5-nano integration for 97% cost reduction with maintained accuracy

### 🔧 **System Features**

- **Flexible Model Selection**: Switch between GPT-5 series models with real-time parameter adjustment
- **Modern User Interface**: Responsive web app with real-time updates and easy navigation
- **Performance & Dev Tools**: Development mode for fast testing and built-in performance monitoring
- **Comprehensive Testing**: Complete test suite with unit, integration, API, and E2E tests
- **Real API Testing**: All tests use actual API calls and real data for authentic validation
- **State Management Tools**: Built-in data export/import, selective clearing, and real-time statistics
- **Text Interaction System**: Advanced text highlighting and LLM interaction capabilities

*Experimental Reasoning Mode and advanced Excel integration coming soon!*

---

## 🔧 **Core System Enhancements**

### 📁 **Document Processing**

- **Smart Upload**: Automatic classification of research papers vs supporting files
- **Batch Processing**: Handle multiple files efficiently with real-time progress tracking
- **Format Support**: PDF and DOCX with robust text extraction and error handling

### 🔍 **Intelligent Management**

- **Duplicate Detection**: Multi-level deduplication using DOI, title, and content analysis
- **Metadata Enrichment**: Automatic enrichment via Semantic Scholar API
- **Type Classification**: Intelligent distinction between main papers and supporting information

---

## 🎛️ Model Configuration

### Available Models

- **GPT-5**: Latest model with reasoning controls and tool chain support
- **GPT-5 Nano**: Lightweight version for fast, simple formatting tasks
- **GPT-5 Mini**: Balanced version with speed and functionality

### Key Parameters

- **Max Tokens**: Response length (1-32,000)
- **Timeout**: Request timeout (10-600 seconds)
- **Reasoning Effort**: Reasoning depth control (minimal/low/medium/high)
- **Verbosity**: Response detail level (low/medium/high)

---

## 🐛 v4.4 Bug Fixes & Improvements

### **Fixed Issues**

- **System Installation**: Fixed `simple_setup.bat` script execution issues and path problems
- **Virtual Environment**: Fixed virtual environment setup process and dependency installation
- **Embedding Model**: Upgraded to more efficient `BAAI/bge-base-en-v1.5` model
- **Citation Management**: Fixed citation cards disappearing after experiment detail generation
- **Proposal Revision**: Fixed chunks from document expansion not being added to citation cards
- **SMILES Integration**: Fixed SMILES drawer failing after proposal revision
- **DOCX Generation**: Fixed chemical table using URL embedding instead of SMILES-drawn structures
- **API Compatibility**: Fixed citations format compatibility in DOCX generation requests

### **Performance Improvements**

- **Embedding Model Optimization**: Upgraded to `BAAI/bge-base-en-v1.5` for better CPU efficiency
- **Reduced Resource Consumption**: Lower CPU usage and memory requirements
- **Enhanced Semantic Understanding**: Improved accuracy for English academic literature
- **Reduced Chunk Retrieval**: Default chunk retrieval reduced from 10 to 3 for better performance
- **Development Mode**: Added k=1 chunk retrieval option for faster testing
- **Smart Caching**: Enhanced citation and chunk management for better user experience

### **Installation Enhancements**

- **Fixed Setup Script**: Resolved `simple_setup.bat` execution issues and path problems
- **Improved Virtual Environment**: Enhanced virtual environment setup and dependency management
- **CPU/GPU Selection**: Smart setup script with installation type selection
- **Error Handling**: Improved error messages and recovery mechanisms
- **Verification**: Enhanced installation verification with PyTorch and CUDA status checks

## 🚀 Quick Start

### Prerequisites

- **Python**: 3.10, 3.11, or 3.12
- **Node.js**: 16.0 or higher
- **Memory**: 8GB RAM minimum (16GB recommended)
- **Storage**: 2GB free space for vector database
- **Testing**: pytest and related dependencies (included in requirements.txt)

### 🎯 One-Click Installation (Windows)

**Recommended: Complete automated setup**

```bash
# Clone and setup everything in one command
simple_setup.bat
```

This script will:

- ✅ Create Python virtual environment (with user choice for existing environments)
- ✅ **Choose CPU or GPU installation** (CPU for compatibility, GPU for performance)
- ✅ Install all Python dependencies with selected version
- ✅ Install Node.js dependencies
- ✅ Verify installation and show system status
- ✅ Open the application in your browser

**🆕 Smart Environment Management**: If a virtual environment already exists, the script will ask whether to:

- **Option 1**: Delete existing environment and create a fresh one
- **Option 2**: Continue with the existing environment

**🆕 CPU vs GPU Installation Options**:

- **CPU Version**: Smaller download, works on all systems (recommended for most users)
- **GPU Version**: Larger download, requires NVIDIA GPU with CUDA support (for performance)

### Manual Installation (All Platforms)

**1. Clone the repository**

```bash
git clone https://github.com/z8z0028z4/AI-research-agent.git
cd AI-research-agent
```

**2. Install Python dependencies**

```bash
# Create virtual environment
double click simple_setup.bat to install venv and all packages
```

**3. Set up environment variables**

```bash
# The system will automatically create a .env file if missing
# You can configure API keys through the Settings page in the web interface

# Or manually create .env file:
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**🆕 Automatic Environment Management**: The system now automatically creates a dummy `.env` file if missing, allowing you to start the application and configure API keys through the web interface.

**4. Launch the application**

**Windows (Recommended):**

```bash
# One-click start (starts both backend and frontend)
start_react.bat

to restart_backend:
run_backend.bat    # Start backend first
```

**🌐 Access the application:**

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 🔑 Environment Configuration

The system now supports automatic environment management:

### **Automatic Setup**

- **Graceful Startup**: System automatically creates a dummy `.env` file if missing
- **Web Interface Configuration**: Configure API keys directly through the Settings page
- **Real-time Validation**: API keys are validated immediately upon entry

### **Manual Setup** (Optional)

Create a `.env` file in the project root directory:

```env
# Required API Keys
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### **API Key Management Features**

- **🔑 Direct Input**: Enter API keys through the web interface
- **✅ Instant Validation**: Real-time API key validation using actual API calls
- **🔄 Automatic Updates**: API key changes take effect immediately
- **📊 Status Display**: View current environment configuration status

---

## 📊 **Performance & Statistics**

### **Document Processing**

- **Batch Size**: Up to 100+ documents per upload
- **Deduplication**: 99%+ accuracy with DOI+type matching
- **Formats**: PDF, DOCX with robust text extraction

### **API Performance**

- **Semantic Scholar**: 95%+ success rate with retry mechanisms
- **Rate Limiting**: Automatic throttling prevents API blocks
- **Metadata**: ~80% venue retrieval success rate

---

## 🧪 Testing

### **Test Suite**

- **Unit Tests**: Individual function and module testing
- **Integration Tests**: Cross-module workflow testing
- **API Tests**: FastAPI endpoint validation
- **E2E Tests**: Complete user workflow testing
- **Performance Tests**: Response time and system performance validation

### **Running Tests**

**Windows (Recommended):**

```bash
# Interactive test menu
run_tests.bat

# Or run specific test types
python tests\run_tests.py --type quick    # Quick core tests
python tests\run_tests.py --type all      # All tests
python tests\run_tests.py --type api      # API tests only
python tests\run_tests.py --type e2e      # End-to-end tests
python tests\run_tests.py --type proposal # Proposal E2E tests
```

**All Platforms:**

```bash
# Run tests
pytest tests/ -v                    # All tests
pytest tests/test_api.py -v         # API tests
pytest tests/test_e2e_real.py -v    # E2E tests
pytest tests/test_e2e_proposal_workflow.py -v  # Proposal E2E tests
```

### **Test Features**

- **Real Testing**: No mocks - tests use actual API calls and real data
- **Comprehensive Coverage**: Tests cover all major features and workflows
- **Error Handling**: Validates system behavior under various error conditions
- **Performance Monitoring**: Tracks response times and system performance

### **Test Results**

- ✅ **All Core Tests Passing**: Unit, integration, and API tests
- ✅ **E2E Tests Passing**: Complete user workflow validation
- ✅ **Proposal E2E Tests**: Full proposal generation workflow testing
- ✅ **Text Interaction Tests**: Complete text highlighting functionality testing
- ✅ **Real API Tests**: All tests use actual API calls and real data
- ✅ **GPT-5-nano Integration Tests**: Cost-effective AI processing validation
- ✅ **Error Handling Tests**: Robust error condition handling
- ✅ **Performance Tests**: Response time validation

---

## 🎯 Usage Guide

### 📋 **Proposal Generator** (Main Feature)

1. **Enter Research Goal**: Describe your research objective
2. **Generate Proposal**: Click "✍️ Generate proposal" to create AI-powered research proposal
3. **Review Results**: View proposal with chemical safety info and citations
4. **Text Interaction**: Select text for LLM explanation and modification
5. **Refine Proposal**: Provide feedback and revise, or expand into detailed experimental plans
6. **Export Document**: Download complete proposal as Word document

### 🔍 **Literature Search**

- **Search Interface**: Query academic databases
- **Citation Management**: Automatic citation formatting and reference tracking
- **Integration**: Use search results in proposal generation

### ⚙️ **Settings & Model Configuration**

- **API Key Management**: Enter and validate OpenAI API key directly in settings
- **Model Selection**: Choose from GPT-5 series models (GPT-5, GPT-5-nano, GPT-5-mini)
- **Cost Optimization**: GPT-5-nano integration for 97% cost reduction
- **Parameter Tuning**: Adjust max_tokens, timeout, and model-specific parameters
- **Real-time Updates**: Changes take effect immediately

### 📥 **Document Upload**

- **Upload Documents**: Drag and drop PDF or Word files
- **Processing**: System chunks, embeds, and stores documents
- **Knowledge Base**: Documents become searchable for proposal generation

### 🔍 **Text Interaction**

- **Text Selection**: Select any text in proposals or documents
- **LLM Explanation**: Get AI-powered explanations of selected text
- **Text Modification**: Request AI to modify or improve selected text
- **Context Preservation**: Maintain context across different pages

---

## 🔧 **Configuration Options**

### **Document Processing**

- **Chunk Size**: 500 characters (configurable)
- **Chunk Overlap**: 50 characters
- **Max Retries**: 3 attempts for API calls
- **Timeout**: 20 seconds for external API calls

### **Deduplication**

- **Primary**: DOI + document type matching
- **Secondary**: Title + document type matching
- **Batch Processing**: Internal duplicate detection
- **Registry Check**: Existing document database comparison

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
└── core/                # RAG implementation (refactored)
```

---

## 🐛 **Critical Bug Fixes**

### **Metadata Extraction**

- ✅ **Fixed**: `'NoneType' object has no attribute 'strip'` errors in duplicate checking
- ✅ **Fixed**: Undefined variable `attempt` in GPT analysis function
- ✅ **Fixed**: LLM response mapping for new output format ("SI", "paper")
- ✅ **Fixed**: Type field inconsistency between metadata extraction and duplicate checking

### **API Integration**

- ✅ **Enhanced**: Semantic Scholar rate limiting handling
- ✅ **Improved**: Error logging and recovery mechanisms
- ✅ **Fixed**: Title-based search venue retrieval issues
- ✅ **Added**: Comprehensive None-value handling throughout the pipeline

---

## 🏗️ **Architecture Improvements**

### **Code Quality**

- **Comprehensive Error Handling**: Try-catch blocks with proper fallback values
- **Improved Logging**: Detailed debug information for troubleshooting
- **Type Safety**: Better handling of optional values and None checks
- **Documentation**: Enhanced inline documentation and function descriptions

### **Performance**

- **Efficient Batch Processing**: Optimized document handling workflows
- **Smart Caching**: Vector database performance improvements
- **Reduced API Calls**: Intelligent deduplication reduces redundant requests
- **Progress Tracking**: Real-time status updates for long-running operations

---

## 🎯 **Production Readiness**

- ✅ **Error Handling**: Comprehensive error recovery mechanisms
- ✅ **Logging**: Detailed operation logging for debugging
- ✅ **Performance**: Optimized for large document sets
- ✅ **Reliability**: Robust API integration with fallbacks
- ✅ **User Experience**: Real-time progress tracking and status updates
- ✅ **Documentation**: Complete installation and usage guides
- ✅ **Testing**: Extensive validation of core workflows

---

## 🛠️ Troubleshooting

### **Common Issues**

1. **Frontend not starting**: `cd frontend && npm install && npm run dev`
2. **Backend API errors**: `cd backend && pip install -r requirements.txt && python main.py`
3. **Port conflicts**: Frontend (3000), Backend (8000), API Docs (8000/api/docs)
4. **Module not found**: `pip install -r requirements.txt --upgrade`
5. **Node.js issues**: Ensure version >= 16.0
6. **API connection**: Check backend on port 8000, verify API keys in `.env`
7. **Model configuration**: Check Settings page for model availability

### **Getting Help**

- **Documentation**: Check README.md and USAGE_GUIDE.md
- **Logs**: Review detailed logs in the application output
- **Issues**: Report bugs via GitHub issues

---

## 🔮 **Future Roadmap**

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
- **🔑 API Key Management**: Integrated API key configuration and validation system

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
- **Europe PMC** for academic search capabilities
- **ChromaDB** for vector database functionality
- **React** and **Ant Design** for the modern UI framework
- **FastAPI** for the backend API framework
- **PubChem** for chemical safety data
- **Europe PMC** for biomedical literature access
- **ITRI AI team** 宗霖、偉倫、素潔 for brainstorming and suggestions

This production release represents months of development, testing, and refinement. Special thanks to all contributors and testers who helped identify and resolve critical issues.

**Ready for Production Use** ✅

This version is stable, tested, and ready for production research workflows.

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/z8z0028z4/AI-research-agent/issues)
- **Documentation**: See `app/ARCHITECTURE_OVERVIEW.md`
- **Learning Guide**: See `app/LEARNING_GUIDE.md`
- **Usage Guide**: See `USAGE_GUIDE.md`

---

*Last updated: 17th, Sep, 2025 - GPT-5-nano Integration & TextHighlight Restoration Release v4.6*
