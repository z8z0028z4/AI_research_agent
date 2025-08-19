@echo off
setlocal enabledelayedexpansion

echo ========================================
echo AI Research Assistant - React Version
echo ========================================
echo 修復內容：
echo - 修復 ChromaDB 配置問題
echo - 排除數據庫文件監控
echo - 異步初始化向量統計
echo - 修復後端模組導入路徑問題
echo.
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

REM Activate virtual environment
call "%VENV_ACTIVATE%" >nul 2>&1

echo Starting AI Research Assistant...
echo.

REM Start backend in a new window (修復 ChromaDB 配置問題)
start "AI Research Assistant Backend" cmd /k "run_backend.bat"
REM Start frontend in a new window
start "AI Research Assistant Frontend" cmd /k "cd /d "%SCRIPT_DIR%frontend" && run_frontend.bat"

echo.
echo Services starting...
echo Backend API: http://localhost:8000
echo Frontend App: http://localhost:3000
echo API Docs: http://localhost:8000/api/docs
echo.
echo Press any key to close this window...
pause >nul
 