# 🧪 AI Research Assistant v4.6 - Security & Installation Enhancement Release

A comprehensive AI-powered research assistant system designed for materials science and chemistry research workflows. **Enhanced Production Release: Complete system with API key management, graceful startup, improved user experience, and comprehensive security updates.**

This production-ready tool combines document ingestion, vector embedding, GPT-based QA with source tracking, experimental data analysis, intelligent content management, and robust configuration management.

---

## 🎉 v4.6 Security & Installation Enhancement Release Highlights

This release focuses on **comprehensive security improvements** and **enhanced installation experience**, ensuring a secure and reliable setup process for all users.

### 🔒 **v4.6 Security & Installation Enhancements**
- **🛡️ Frontend Security Fixes**: Comprehensive security vulnerability remediation
  - Fixed high-risk axios DoS attack vulnerability
  - Resolved vite file serving security issues
  - Updated all frontend dependencies to secure versions
  - Implemented automatic security audit in installation scripts
- **⚙️ Enhanced Installation Scripts**: Improved setup process with security checks
  - Updated `simple_setup.bat` with comprehensive security vulnerability fixes
  - Enhanced `install_frontend.bat` with automatic security audit
  - Improved `dependency_manager.py` with security validation
  - Added error handling and user-friendly security status reporting
- **🔧 PowerShell Compatibility**: Fixed Windows PowerShell execution issues
  - Resolved batch file execution in PowerShell environments
  - Added proper path handling for Windows systems
  - Improved cross-platform compatibility
- **📦 Dependency Management**: Streamlined and secured package management
  - Automatic npm audit fix integration
  - Real-time security vulnerability detection
  - Enhanced dependency update workflow
- **🧹 Project Structure Cleanup**: Optimized codebase organization
  - Removed unused test files and directories
  - Cleaned up outdated documentation
  - Simplified project structure for better maintainability
- **💬 Text Highlight Popup LLM Integration**: Interactive text analysis feature
  - Text highlighting with popup LLM responses
  - Context-aware AI answers for selected text
  - Seamless integration with document analysis workflow
  - Enhanced user interaction and knowledge extraction

---

## ✨ Key Features

### 🎯 **Core Features**
- **AI Proposal Generator**: Create and refine research proposals with automatic chemical safety info and citation tracking
- **Smart Document Management**: Upload, classify, and deduplicate research files (PDF, DOCX) with automatic metadata enrichment
- **Knowledge Base & Embedding**: Build searchable knowledge base using advanced embeddings (CPU-optimized)
- **Chemical Structure Support**: Visualize and insert chemical structures (SMILES) into Word documents
- **💬 Text Highlight Popup LLM**: Interactive text analysis with AI-powered popup responses
- **State Persistence**: Automatic saving and restoration of all generated content across tab switches and page refreshes

### 🔧 **System Features**
- **Flexible Model Selection**: Switch between GPT-5 series models with real-time parameter adjustment
- **Modern User Interface**: Responsive web app with real-time updates and easy navigation
- **Enhanced Security**: Comprehensive security vulnerability fixes and automatic audit
- **Cross-Platform Compatibility**: Improved Windows PowerShell and installation support

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

## 🐛 Recent Bug Fixes & Improvements

### **Recent Improvements**
- **Security Fixes**: Fixed high-risk axios and vite vulnerabilities
- **Installation Scripts**: Enhanced setup process with automatic security audit
- **PowerShell Compatibility**: Fixed Windows PowerShell execution issues
- **Text Highlight Feature**: Added interactive popup LLM responses for text analysis
- **Performance**: Upgraded to more efficient embedding model
- **Project Cleanup**: Removed unused files and simplified structure

## 🚀 Quick Start

### Prerequisites
- **Python**: 3.10, 3.11, or 3.12
- **Node.js**: 16.0 or higher
- **Memory**: 8GB RAM minimum (16GB recommended)

### 🎯 One-Click Installation (Windows)

**Recommended: Complete automated setup**
```bash
# Clone and setup everything in one command
simple_setup.bat
```

This script will:
- ✅ Create Python virtual environment
- ✅ Choose CPU or GPU installation
- ✅ Install all dependencies with security fixes
- ✅ Verify installation and show system status

### Launch Application
```bash
# Start both backend and frontend
start_react.bat
```

**🌐 Access the application:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Environment Configuration
The system automatically creates a `.env` file if missing. Configure API keys through the Settings page in the web interface.

---

## 🧪 Testing
```bash
# Run all tests
run_tests.bat

# Or run specific tests
pytest tests/ -v
```

---

## 🎯 Usage Guide

### 📋 **Main Features**
1. **Proposal Generator**: Enter research goal → Generate AI-powered proposal → Export to Word
2. **Literature Search**: Query academic databases with citation management
3. **Document Upload**: Upload PDF/DOCX files for knowledge base building
4. **Text Highlight**: Select text to get AI-powered popup responses
5. **Settings**: Configure API keys and model parameters through web interface

### 🔧 **Configuration**
- **API Keys**: Configure through Settings page (automatic .env creation)
- **Model Selection**: Choose from GPT-5 series models
- **Document Processing**: Automatic chunking and embedding
- **Security**: Automatic vulnerability scanning and fixes

---

## 🏗️ Architecture
```
frontend/          # React 18 + Vite + Ant Design
├── src/pages/     # Main application pages
├── src/components/ # Reusable UI components
└── src/services/  # API integration

backend/           # FastAPI backend
├── api/routes/    # API endpoints
├── core/          # Core configuration
└── services/      # Business logic
```

---

## 🛠️ Troubleshooting

### **Common Issues**
1. **Frontend not starting**: `cd frontend && npm install && npm run dev`
2. **Backend API errors**: `cd backend && pip install -r requirements.txt && python main.py`
3. **Port conflicts**: Frontend (3000), Backend (8000)
4. **API connection**: Check backend on port 8000, verify API keys in Settings

### **Getting Help**
- **Documentation**: Check README.md
- **Logs**: Review application output
- **Issues**: Report bugs via GitHub issues

---

## 🔮 **Future Roadmap**

### 🔍 **Enhanced Features**
- **Improved Retrieval**: Better search and ranking algorithms
- **Local LLM Integration**: Offline capabilities with local models

### 🎯 **Interactive Features**
- **Text Highlighting**: Select text for LLM explanation and modification
- **Proposal Mode Integration**: Direct text editing and modification in proposal mode

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI** for GPT models and API
- **LangChain** for LLM framework and tools
- **FastAPI** for robust backend API framework
- **React** and **Ant Design** for modern frontend interface
- **ChromaDB** for vector database and embedding storage

---

*Last updated: September 2025 - Security & Installation Enhancement Release v4.6*
