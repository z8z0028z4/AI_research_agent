# Contributing to AI Research Assistant

Thank you for your interest in contributing to the AI Research Assistant project! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or 3.11
- Git
- Basic knowledge of Python, AI/ML, and research workflows

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/AI-research-agent.git
   cd AI-research-agent
   ```

2. **Create a virtual environment**
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
   pip install -r research_agent/requirements.txt[dev]
   ```

4. **Set up environment variables**
   ```bash
   cp research_agent/env.example research_agent/.env
   # Edit .env with your API keys
   ```

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and single-purpose

### Testing
- Write tests for new features
- Ensure all tests pass before submitting
- Use pytest for testing
- Aim for good test coverage

### Documentation
- Update README.md for user-facing changes
- Add comments for complex logic
- Update docstrings when modifying functions
- Keep architecture documentation current

## 📝 Making Changes

### Branch Naming
Use descriptive branch names:
- `feature/new-feature-name`
- `bugfix/issue-description`
- `docs/documentation-update`

### Commit Messages
Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test your changes**
   ```bash
   # Run tests
   pytest research_agent/app/
   
   # Check code style
   black research_agent/app/
   flake8 research_agent/app/
   
   # Test the application
   cd research_agent
   python app/main.py
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Submit Pull Request**
   - Provide clear description of changes
   - Link any related issues
   - Include screenshots for UI changes

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest research_agent/app/

# Run specific test file
pytest research_agent/app/test_file.py

# Run with coverage
pytest --cov=research_agent/app research_agent/app/
```

### Test Structure
- Unit tests for individual functions
- Integration tests for module interactions
- End-to-end tests for complete workflows

## 📚 Documentation

### Code Documentation
- Use Google-style docstrings
- Include type hints
- Document complex algorithms
- Explain business logic

### User Documentation
- Update README.md for new features
- Add usage examples
- Include troubleshooting guides
- Keep installation instructions current

## 🔍 Code Review Process

### What We Look For
- **Functionality**: Does it work as intended?
- **Code Quality**: Is it well-written and maintainable?
- **Testing**: Are there adequate tests?
- **Documentation**: Is it well-documented?
- **Performance**: Does it perform efficiently?
- **Security**: Are there any security concerns?

### Review Checklist
- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No breaking changes (or properly documented)
- [ ] Performance impact is considered
- [ ] Security implications are addressed

## 🐛 Reporting Issues

### Bug Reports
When reporting bugs, please include:
- **Description**: Clear description of the issue
- **Steps to reproduce**: Detailed steps to reproduce
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**: OS, Python version, dependencies
- **Screenshots**: If applicable

### Feature Requests
When requesting features, please include:
- **Description**: Clear description of the feature
- **Use case**: Why this feature is needed
- **Proposed implementation**: How it might work
- **Alternatives considered**: Other approaches

## 🏗️ Architecture

### Project Structure
```
research_agent/
├── app/                    # Main application code
│   ├── main.py            # Entry point
│   ├── research_gui.py    # Streamlit GUI
│   ├── rag_core.py        # RAG implementation
│   ├── knowledge_agent.py # Knowledge processing
│   └── ...                # Other modules
├── requirements.txt        # Dependencies
├── env.example            # Environment template
└── README.md              # Documentation
```

### Key Components
- **RAG Core**: Retrieval-Augmented Generation implementation
- **Knowledge Agent**: Document processing and Q&A
- **GUI**: Streamlit-based user interface
- **Vector Database**: ChromaDB for embeddings
- **Search Integration**: Perplexity and Europe PMC

## 🤝 Community Guidelines

### Communication
- Be respectful and inclusive
- Use clear, constructive language
- Ask questions when unsure
- Help others when possible

### Collaboration
- Share knowledge and best practices
- Review others' code constructively
- Provide feedback on issues and PRs
- Contribute to discussions

## 📞 Getting Help

- **Issues**: Use GitHub Issues for bugs and feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check README.md and architecture docs
- **Code**: Review existing code for examples

## 🎯 Areas for Contribution

### High Priority
- Performance optimization
- Additional document formats
- Enhanced error handling
- Improved UI/UX
- More comprehensive testing

### Medium Priority
- Additional search integrations
- Export functionality
- Batch processing
- API endpoints
- Docker support

### Low Priority
- Documentation improvements
- Code refactoring
- Minor bug fixes
- Style improvements

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AI Research Assistant! 🚀 