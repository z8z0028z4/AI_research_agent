@echo off
echo ========================================
echo AI Research Assistant - Installation
echo ========================================
echo.

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10, 3.11, or 3.12 from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking version...
python -c "import sys; print('Python version:', sys.version)" 2>nul
if errorlevel 1 (
    echo ERROR: Python version check failed
    pause
    exit /b 1
)

echo.
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Setting up environment file...
if not exist "research_agent\.env" (
    copy "env.example" "research_agent\.env"
    echo.
    echo IMPORTANT: Please edit research_agent\.env and add your API keys:
    echo - OPENAI_API_KEY: Get from https://platform.openai.com/api-keys
    echo - PERPLEXITY_API_KEY: Get from https://www.perplexity.ai/settings/api
    echo.
) else (
    echo Environment file already exists
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo To start the application:
echo 1. run.bat
echo 2. python app\main.py
echo.
echo The application will open at http://localhost:8501
echo.
pause 