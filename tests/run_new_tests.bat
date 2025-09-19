@echo off
REM 新增測試功能運行腳本
REM 測試日期: 2025/9/19
REM 作者: AI Research Agent Team

echo ========================================
echo 新增測試功能運行腳本 (2025/9/19)
echo ========================================
echo.

REM 檢查 Python 環境
echo [1/4] 檢查 Python 環境...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python 未安裝或不在 PATH 中
    pause
    exit /b 1
)
echo ✅ Python 環境正常

REM 檢查測試依賴
echo.
echo [2/4] 檢查測試依賴...
python -c "import pytest" 2>nul
if %errorlevel% neq 0 (
    echo ❌ pytest 未安裝，正在安裝...
    pip install pytest pytest-cov pytest-mock
    if %errorlevel% neq 0 (
        echo ❌ 依賴安裝失敗
        pause
        exit /b 1
    )
)
echo ✅ 測試依賴正常

REM 運行文獻搜尋測試
echo.
echo [3/4] 運行文獻搜尋測試...
echo 測試文件: test_paper_search.py
python -m pytest test_paper_search.py -v --tb=short
if %errorlevel% neq 0 (
    echo ❌ 文獻搜尋測試失敗
    pause
    exit /b 1
)
echo ✅ 文獻搜尋測試通過

REM 運行化學品搜尋測試
echo.
echo [4/4] 運行化學品搜尋測試...
echo 測試文件: test_chemical_search.py
python -m pytest test_chemical_search.py -v --tb=short
if %errorlevel% neq 0 (
    echo ❌ 化學品搜尋測試失敗
    pause
    exit /b 1
)
echo ✅ 化學品搜尋測試通過

echo.
echo ========================================
echo 🎉 所有新增測試功能運行成功！
echo ========================================
echo.
echo 測試摘要:
echo - 文獻搜尋測試: ✅ 通過
echo - 化學品搜尋測試: ✅ 通過
echo - 測試日期: 2025/9/19
echo.
echo 如需運行完整測試套件，請使用: run_tests.bat
echo 如需查看覆蓋率報告，請使用: run_tests.bat --cov
echo.
pause