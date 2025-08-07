# Changelog

All notable changes to the AI Research Assistant project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation updates
- Installation scripts for Windows and Unix systems
- Setup.py for pip installation
- Contributing guidelines
- License file (MIT)
- Gitignore file for sensitive data protection

### Changed
- Updated requirements.txt with all missing dependencies
- Improved README.md with comprehensive documentation
- Enhanced project structure documentation

## [2.0.0] - 2025-01-XX

### Added
- **Experimental Reasoning Mode**: Dual retriever architecture combining literature and experimental data
- **Chemical Safety Integration**: PubChem data integration with NFPA hazard codes
- **Enhanced Document Processing**: Support for Excel files and experimental data
- **Academic Search**: Perplexity API integration for real-time literature search
- **Europe PMC Integration**: Direct access to biomedical literature
- **Citation Tracking**: Numbered references with source document links
- **Vector Database**: ChromaDB integration for semantic search
- **Streamlit GUI**: Modern web interface with tabbed navigation
- **CLI Mode**: Command-line interface for automation
- **File Upload**: Drag-and-drop support for documents
- **Real-time Processing**: Live status updates and progress indicators

### Changed
- **Embedding Model**: Upgraded to `nomic-ai/nomic-embed-text-v1.5` for academic content
- **LLM Integration**: Enhanced GPT-4 integration with better prompting
- **Document Chunking**: Improved chunking with metadata preservation
- **Error Handling**: Comprehensive error handling and user feedback
- **Performance**: Optimized vector search and document processing

### Fixed
- SSL certificate handling for enterprise environments
- Memory optimization for large document sets
- Cross-platform compatibility issues
- API rate limiting and error recovery

## [1.0.0] - 2024-XX-XX

### Added
- Initial release of AI Research Assistant
- Basic document processing capabilities
- Simple Q&A functionality
- PDF and Word document support
- Basic vector embedding
- Streamlit web interface

---

## Version History

- **v2.0.0**: Major feature release with experimental reasoning, chemical safety, and academic search
- **v1.0.0**: Initial release with basic document processing and Q&A capabilities

## Migration Guide

### From v1.0.0 to v2.0.0

1. **Update Dependencies**
   ```bash
   pip install -r research_agent/requirements.txt --upgrade
   ```

2. **Environment Variables**
   - Add `PERPLEXITY_API_KEY` to your `.env` file
   - Update to new embedding model configuration

3. **Vector Database**
   - Existing embeddings may need regeneration with new model
   - Run document processing again for optimal performance

4. **Configuration**
   - Review `config.py` for new options
   - Update any custom configurations

## Deprecation Notices

- **v2.2.0**: Old vector database format will be deprecated

## Breaking Changes

### v2.0.0
- Updated vector database schema
- Modified configuration file structure
- Changed API response format for citations

## Security Updates

### v2.0.0
- Enhanced SSL certificate handling
- Improved API key security
- Added input validation
- Implemented rate limiting

---

For detailed information about each release, see the [GitHub releases page](https://github.com/yourusername/AI-research-agent/releases). 