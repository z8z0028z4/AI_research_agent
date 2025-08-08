@echo off
echo ========================================
echo    AI Research Assistant Backend
echo    完整後端重啟腳本
echo ========================================
echo.

REM 停止所有 Python 進程
echo 🔄 正在停止現有的 Python 進程...
taskkill /f /im python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ 已停止現有進程
) else (
    echo ℹ️ 沒有找到需要停止的進程
)
echo.

REM 等待一下確保進程完全停止
timeout /t 2 /nobreak >nul

REM 檢查虛擬環境
echo 🔍 檢查虛擬環境...
if exist "venv\Scripts\activate.bat" (
    echo ✅ 找到 venv 虛擬環境
    set VENV_PATH=venv
) else if exist "venv_company\Scripts\activate.bat" (
    echo ✅ 找到 venv_company 虛擬環境
    set VENV_PATH=venv_company
) else (
    echo ❌ 未找到虛擬環境，請先運行 install.bat
    pause
    exit /b 1
)

REM 啟動後端服務
echo 🚀 正在啟動後端服務...
echo 📍 後端地址: http://localhost:8000
echo 📍 API 文檔: http://localhost:8000/api/docs
echo.

cd backend

REM 激活虛擬環境並啟動服務
call "..\%VENV_PATH%\Scripts\activate.bat"
python main.py

pause 