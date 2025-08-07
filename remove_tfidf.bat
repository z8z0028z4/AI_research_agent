@echo off
echo ========================================
echo Removing TF-IDF related files and code
echo ========================================
echo.

echo Cleaning up TF-IDF cache files...
if exist "research_agent\app\__pycache__\tfidf_embedding.cpython-*.pyc" (
    del "research_agent\app\__pycache__\tfidf_embedding.cpython-*.pyc"
    echo ✓ TF-IDF cache files removed
)

echo.
echo Checking for any remaining TF-IDF references...
findstr /s /i "tfidf" research_agent\app\*.py
if %errorlevel% equ 0 (
    echo ⚠️  Found remaining TF-IDF references in Python files
) else (
    echo ✅ No TF-IDF references found in Python files
)

echo.
echo ========================================
echo TF-IDF cleanup completed!
echo ========================================
echo.
echo The following changes were made:
echo - Removed TF-IDF import and fallback logic from rag_core.py
echo - Updated config.py comments
echo - Removed TF-IDF cache files
echo - Updated CHANGELOG.md
echo.
echo The system now uses only Nomic AI embeddings.
echo.
pause 