@echo off
setlocal enabledelayedexpansion

echo ========================================
echo AI Research Assistant - Simple Setup
echo ========================================
echo This script will create a virtual environment and install all dependencies.
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
    echo [ERROR] Python not found. Please install Python 3.10+ and ensure it's in your PATH.
    pause
    exit /b 1
)
echo [OK] Python found:
python --version
echo.

REM Set virtual environment path
set "VENV_PATH=%~dp0.venv"
set "VENV_ACTIVATE=%VENV_PATH%\Scripts\activate.bat"

echo Virtual environment will be created at: %VENV_PATH%
echo.

REM Create virtual environment if it doesn't exist
if not exist "%VENV_PATH%" (
    echo Creating virtual environment...
    python -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created successfully!
) else (
    echo Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_ACTIVATE%"
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)
echo [OK] Virtual environment activated.
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [ERROR] Failed to upgrade pip.
    pause
    exit /b 1
)
echo.

REM Install main requirements
echo Installing main requirements from requirements.txt...
if exist "requirements.txt" (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install packages from requirements.txt.
        pause
        exit /b 1
    )
    echo [OK] Main requirements installed successfully.
) else (
    echo [ERROR] requirements.txt not found.
    pause
    exit /b 1
)
echo.

REM Install frontend dependencies
echo Installing frontend dependencies...
if exist "frontend\package.json" (
    echo Running npm install in frontend directory...
    cd frontend
    npm install
    if errorlevel 1 (
        echo [WARNING] npm install failed. Please check your Node.js/npm setup.
        echo Continuing with setup...
    ) else (
      echo [OK] Frontend dependencies installed successfully!
    )
    cd ..
) else (
    echo [WARNING] package.json not found in frontend directory. Skipping frontend installation.
)
echo.

REM Create configuration file
echo Creating configuration file...
(
    echo VENV_PATH="%VENV_PATH%"
    echo VENV_ACTIVATE="%VENV_ACTIVATE%"
) > .venv_config
echo [OK] Configuration file created: .venv_config
echo.

echo ========================================
echo  Setup script completed. Verifying...
echo ========================================
echo.
python dependency_manager.py
set "VERIFY_CODE=%ERRORLEVEL%"

echo.
echo ========================================
if %VERIFY_CODE% EQU 0 (
    echo [SUCCESS] Setup and verification completed successfully!
) else (
    echo [ERROR] Verification failed. Please review the errors above.
)
echo ========================================
echo.
echo To start the application:
echo 1. Backend: restart_backend.bat
echo 2. Frontend: start_react.bat
echo.
echo Press any key to exit...
pause >nul
exit /b %VERIFY_CODE%