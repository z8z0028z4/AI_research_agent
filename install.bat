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
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)

echo Node.js found. Checking version...
node --version
if errorlevel 1 (
    echo ERROR: Node.js version check failed
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
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Installing backend dependencies...
cd backend
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install backend dependencies
    pause
    exit /b 1
)
cd ..

echo.
echo Installing frontend dependencies...
cd frontend
npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
cd ..

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
echo To start the React application:
echo 1. start_react_app.bat (Recommended - starts both frontend and backend)
echo.
echo Or start services separately:
echo 2. Backend: cd backend && run_api.bat
echo 3. Frontend: cd frontend && run_frontend.bat
echo.
echo The application will be available at:
echo - Frontend: http://localhost:3000
echo - Backend API: http://localhost:8000
echo - API Documentation: http://localhost:8000/api/docs
echo.
echo For Streamlit version (legacy):
echo - run.bat
echo - Available at: http://localhost:8501
echo.
pause 