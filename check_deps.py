#!/usr/bin/env python3
"""
Simple dependency checker for AI Research Assistant
"""

import sys
import importlib

def check_dependencies():
    """Check if critical dependencies are installed"""
    # 定義依賴包和對應的模組名稱
    critical_deps = [
        ('langchain', 'langchain'),
        ('langchain-openai', 'langchain_openai'),
        ('langchain-community', 'langchain_community'),
        ('langchain-core', 'langchain_core'),
        ('langchain-huggingface', 'langchain_huggingface'),
        ('openai', 'openai'),
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('requests', 'requests'),
        ('python-dotenv', 'dotenv'),  # 包名是 python-dotenv，模組名是 dotenv
        ('torch', 'torch'),
        ('transformers', 'transformers'),
        ('sentence-transformers', 'sentence_transformers'),
        ('tokenizers', 'tokenizers'),
        ('huggingface-hub', 'huggingface_hub'),
        ('chromadb', 'chromadb'),
        ('scipy', 'scipy'),
        ('scikit-learn', 'sklearn'),
        ('einops', 'einops')
    ]
    
    missing_deps = []
    
    for package_name, module_name in critical_deps:
        try:
            importlib.import_module(module_name)
            print(f'✅ {package_name}')
        except ImportError:
            print(f'❌ {package_name}')
            missing_deps.append(package_name)
    
    if missing_deps:
        print(f'\n❌ Missing dependencies: {", ".join(missing_deps)}')
        return False
    else:
        print('\n✅ All critical dependencies are available')
        return True

def test_critical_imports():
    """Test critical imports that are known to cause issues"""
    print("\nTesting critical imports...")
    
    # Test sentence-transformers specifically
    try:
        import sentence_transformers
        print("✅ sentence-transformers imported successfully")
    except ImportError as e:
        print(f"❌ sentence-transformers import failed: {e}")
        return False
    
    # Test langchain-huggingface specifically
    try:
        import langchain_huggingface
        print("✅ langchain-huggingface imported successfully")
    except ImportError as e:
        print(f"❌ langchain-huggingface import failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Checking dependencies...")
    success = check_dependencies()
    
    if success:
        test_success = test_critical_imports()
        if not test_success:
            print("\n⚠️  Some critical imports failed. Run fix_sentence_transformers.bat to resolve.")
            sys.exit(1)
    
    sys.exit(0 if success else 1)
