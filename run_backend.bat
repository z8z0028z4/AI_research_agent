@echo off
setlocal enabledelayedexpansion
echo ========================================
echo    AI Research Assistant Backend
echo ========================================
echo.

REM 切到專案根
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM 載入 venv 設定
set "VENV_PATH="
set "VENV_ACTIVATE="
if exist ".venv_config" (
    for /f "tokens=1,2 delims==" %%a in (.venv_config) do (
        if "%%a"=="VENV_PATH" set "VENV_PATH=%%b"
        if "%%a"=="VENV_ACTIVATE" set "VENV_ACTIVATE=%%b"
    )
)

REM 啟動 venv
call "%VENV_ACTIVATE%" >nul 2>&1

echo Starting backend service...
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload --log-level info
