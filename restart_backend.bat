@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    AI Research Assistant Backend
echo    後端服務重啟腳本
echo ========================================
echo.

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Load virtual environment configuration
set "VENV_PATH="
set "VENV_ACTIVATE="

if exist ".venv_config" (
    for /f "tokens=1,2 delims==" %%a in (.venv_config) do (
        if "%%a"=="VENV_PATH" set "VENV_PATH=%%b"
        if "%%a"=="VENV_ACTIVATE" set "VENV_ACTIVATE=%%b"
    )
)

REM Check if virtual environment exists and setup if needed
if not exist "%VENV_PATH%" (
    echo Setting up virtual environment...
    call venv_setup.bat >nul 2>&1
    
    REM Reload configuration after setup
    if exist ".venv_config" (
        for /f "tokens=1,2 delims==" %%a in (.venv_config) do (
            if "%%a"=="VENV_PATH" set "VENV_PATH=%%b"
            if "%%a"=="VENV_ACTIVATE" set "VENV_ACTIVATE=%%b"
        )
    )
)

REM Stop existing Python processes
echo Stopping existing processes...
taskkill /f /im python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Activate virtual environment
call "%VENV_ACTIVATE%" >nul 2>&1

echo Starting backend service...
echo Backend: http://localhost:8000
echo API Docs: http://localhost:8000/api/docs
echo.

REM Start backend service
if exist "backend\main.py" (
    uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
) else if exist "main.py" (
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level info
) else (
    echo ERROR: Backend main.py not found
    pause
    exit /b 1
) 