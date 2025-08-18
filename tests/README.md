# Tests Directory

This directory contains all test files for the AI Research Agent project.

## 📋 Test Files Overview

### Core Functionality Tests
- **`test_fixes.py`** - Basic functionality tests for settings manager and LLM calls
- **`test_fixed_rag_core.py`** - Tests for RAG core functionality including LLM calls and proposal generation
- **`test_improved_rag_core.py`** - Enhanced RAG core testing
- **`test_model_config.py`** - Model configuration and LLM call testing

### GPT-5 Specific Tests
- **`test_gpt5_parameters.py`** - GPT-5 parameter detection and adaptation testing
- **`test_gpt5_response.py`** - Basic GPT-5 response testing
- **`test_gpt5_reasoning_simple.py`** - Simple GPT-5 reasoning mode testing
- **`test_gpt5_improved_handling.py`** - Improved GPT-5 handling with retry logic
- **`test_gpt5_incomplete_handling.py`** - Testing incomplete response handling for GPT-5

### Workflow Tests
- **`test_full_proposal_workflow.py`** - Complete proposal generation workflow testing
- **`test_proposal_workflow.py`** - Proposal workflow testing
- **`test_simple_proposal.py`** - Simple proposal testing

### Settings and Configuration Tests
- **`test_dynamic_params.py`** - Dynamic parameter management testing
- **`test_frontend_settings.py`** - Frontend settings functionality testing
- **`test_model_specific_params.py`** - Model-specific parameter validation
- **`test_settings_persistence.py`** - Settings persistence testing

### Debug and Development Tests
- **`test_reasoning_mode_debug.py`** - Debugging tests for reasoning mode functionality

## 🚀 Running Tests

### Individual Test Files
```bash
# Run a specific test file
python tests/test_fixes.py
python tests/test_gpt5_parameters.py
```

### All Tests (if using pytest)
```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v
```

## 📝 Test Categories

### 🔧 **Core System Tests**
- Basic functionality verification
- LLM integration testing
- RAG system testing

### 🤖 **GPT-5 Integration Tests**
- Parameter handling
- Response processing
- Error handling
- Reasoning mode testing

### ⚙️ **Configuration Tests**
- Settings management
- Parameter persistence
- Model configuration
- Frontend-backend integration

### 🔄 **Workflow Tests**
- End-to-end proposal generation
- Complete system workflows
- Integration testing

## 🎯 Test Purposes

Each test file serves specific purposes:

1. **Verification**: Ensure core functionality works correctly
2. **Regression Testing**: Prevent breaking changes
3. **Integration Testing**: Test component interactions
4. **Performance Testing**: Monitor system performance
5. **Error Handling**: Test error scenarios and recovery

## 📊 Test Results

When running tests, look for:
- ✅ **Pass**: Test completed successfully
- ❌ **Fail**: Test failed - check error messages
- ⚠️ **Warning**: Test passed but with warnings
- 🔄 **Retry**: Test retried due to temporary issues

## 🔧 Maintenance

- Keep tests updated when adding new features
- Add new tests for new functionality
- Remove obsolete tests when features are deprecated
- Update test data when API responses change 