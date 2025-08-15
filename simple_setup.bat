@echo off
setlocal enabledelayedexpansion

echo ========================================
echo AI Research Assistant - Simple Setup
echo ========================================
echo.

REM Get current directory
set "PROJECT_DIR=%~dp0"
cd /d "%PROJECT_DIR%"
echo Working directory: %CD%
echo.

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.10+
    pause
    exit /b 1
)
echo Python found: 
python --version
echo.

REM Set virtual environment path
set "VENV_PATH=C:\ai_research_venv"
set "VENV_ACTIVATE=%VENV_PATH%\Scripts\activate.bat"

echo Virtual environment will be created at: %VENV_PATH%
echo.

REM Create virtual environment if it doesn't exist
if not exist "%VENV_PATH%" (
    echo Creating virtual environment...
    python -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
) else (
    echo Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_ACTIVATE%"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated.
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
echo.

REM Install PyTorch
echo Installing PyTorch...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
echo.

REM Install requirements
echo Installing requirements...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo Requirements installed.
) else (
    echo WARNING: requirements.txt not found
)
echo.

REM Install backend requirements
if exist "backend\requirements.txt" (
    echo Installing backend requirements...
    pip install -r backend\requirements.txt
    echo Backend requirements installed.
)
echo.

REM Install frontend dependencies (at the end)
echo Installing frontend dependencies...
if exist "frontend" (
    if exist "frontend\package.json" (
        echo Running npm install in frontend directory...
        cd frontend
        npm install
        if errorlevel 1 (
            echo WARNING: npm install failed, but continuing...
        ) else (
            echo Frontend dependencies installed successfully!
        )
        cd ..
        echo Returned to project root: %CD%
    ) else (
        echo WARNING: package.json not found in frontend
    )
) else (
    echo WARNING: frontend directory not found
)
echo.

REM Create configuration file
echo Creating configuration file...
echo VENV_PATH=%VENV_PATH% > .venv_config
echo VENV_ACTIVATE=%VENV_ACTIVATE% >> .venv_config
echo Configuration file created: .venv_config
echo.

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Virtual environment: %VENV_PATH%
echo.

REM Verify dependencies
echo ========================================
echo Verifying dependencies...
echo ========================================
echo.
python dependency_manager.py
echo.

echo ========================================
echo Setup and verification completed!
echo ========================================
echo.
echo To start the application:
echo 1. Backend: restart_backend.bat
echo 2. Frontend: start_react.bat
echo.
echo Press any key to exit...
pause >nul
