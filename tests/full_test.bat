@echo off
chcp 65001 >nul
echo.
echo 🧪 AI Research Agent 完整測試
echo ================================
echo.

:: 檢查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：未找到 Python
    pause
    exit /b 1
)

:: 檢查是否在 tests 目錄
if not exist "test_core_modules.py" (
    echo ❌ 錯誤：請在 tests 目錄中運行此腳本
    pause
    exit /b 1
)

:: 檢查項目根目錄
if not exist "..\backend" (
    echo ❌ 錯誤：未找到 backend 目錄，請確保在正確的項目結構中
    pause
    exit /b 1
)

:: 安裝依賴
echo 🔍 檢查並安裝依賴...
pip install pytest pytest-cov fastapi httpx

echo.
echo 🚀 開始完整測試套件...
echo.

:: 運行所有測試
python -m pytest . -v --tb=short

echo.
echo ✅ 完整測試完成！
pause 