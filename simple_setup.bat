@echo off
REM =================================================================
REM AI Research Assistant - One-Click Setup Script
REM Automatically completes all environment setup, no user selection required
REM 
REM Features:
REM 1. Create virtual environment at C:\ai_research_venv
REM 2. Generate .venv_config for correct environment reference
REM 3. Install all backend Python dependencies
REM 4. Install frontend Node.js dependencies
REM 5. Verify installation
REM =================================================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ========================================
echo AI Research Assistant - One-Click Setup
echo ========================================
echo Starting automatic environment setup...
echo.

REM =================================================================
REM Step 1: Create Python Virtual Environment
REM =================================================================
echo [1/5] Creating Python virtual environment...
set VENV_PATH=C:\ai_research_venv

if exist "%VENV_PATH%" (
    echo Virtual environment already exists, removing old environment...
    rmdir /s /q "%VENV_PATH%"
)

echo Creating new virtual environment at %VENV_PATH%...
python -m venv "%VENV_PATH%"

if errorlevel 1 (
    echo ERROR: Failed to create virtual environment! Please make sure Python is installed.
    pause
    exit /b 1
)

echo ✅ Virtual environment created successfully!

REM =================================================================
REM Step 2: Create .venv_config File
REM =================================================================
echo [2/5] Creating environment config file...

echo VENV_PATH=%VENV_PATH% > .venv_config
echo VENV_ACTIVATE=%VENV_PATH%\Scripts\activate.bat >> .venv_config
echo. >> .venv_config

echo ✅ .venv_config file created!

REM =================================================================
REM Step 3: Upgrade pip and Install Backend Dependencies
REM =================================================================
echo [3/5] Activating virtual environment and installing backend dependencies...

call "%VENV_PATH%\Scripts\activate.bat"

echo Upgrading pip to the latest version...
python -m pip install --upgrade pip

if errorlevel 1 (
    echo ERROR: Failed to upgrade pip!
    pause
    exit /b 1
)

echo Installing backend Python dependencies (this may take a few minutes)...
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install Python dependencies!
    echo Please check the requirements.txt file and your network connection.
    pause
    exit /b 1
)

echo ✅ Backend dependencies installed!

REM =================================================================
REM Step 4: Install Frontend Dependencies
REM =================================================================
echo [4/5] Installing frontend dependencies...

if not exist "frontend" (
    echo ERROR: frontend directory does not exist!
    pause
    exit /b 1
)

cd frontend

if not exist "package.json" (
    echo ERROR: package.json file does not exist!
    cd ..
    pause
    exit /b 1
)

echo Installing frontend Node.js dependencies (this may take a few minutes)...
npm install

if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies!
    echo Please make sure Node.js and npm are installed.
    cd ..
    pause
    exit /b 1
)

echo Checking and fixing security vulnerabilities...
npm audit fix --audit-level=moderate

echo ✅ Frontend dependencies installed!
cd ..

REM =================================================================
REM Step 5: Verify Installation
REM =================================================================
echo [5/5] Verifying installation...

echo Verifying Python environment...
call "%VENV_PATH%\Scripts\activate.bat"
python --version
pip --version

echo.
echo Verifying key Python packages...
python -c "import fastapi; print('✅ FastAPI:', fastapi.__version__)" 2>nul || echo "❌ FastAPI not installed"
python -c "import langchain; print('✅ LangChain:', langchain.__version__)" 2>nul || echo "❌ LangChain not installed"
python -c "import openai; print('✅ OpenAI:', openai.__version__)" 2>nul || echo "❌ OpenAI not installed"

echo.
echo Verifying frontend environment...
cd frontend
npm --version
cd ..

REM =================================================================
REM Setup Complete
REM =================================================================
echo.
echo ========================================
echo 🎉 Setup Complete!
echo ========================================
echo.
echo Virtual environment location: %VENV_PATH%
echo Config file: .venv_config
echo.
echo Next steps:
echo 1. Use restart_backend.bat to start the backend service
echo 2. Use start_react.bat to start the frontend interface
echo 3. Or check QUICK_START.md for more usage instructions
echo.
echo Note: Please make sure you have configured API keys in the .env file
echo.

pause
