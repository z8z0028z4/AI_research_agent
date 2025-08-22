@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo 🧪 AI Research Agent 測試套件
echo ========================================
echo.

:: 檢查是否在正確的目錄
if not exist "test_core_modules.py" (
    echo ❌ 錯誤：請在 tests/ 目錄中運行此腳本
    echo 當前目錄：%CD%
    echo 請執行：cd tests
    pause
    exit /b 1
)

:: 檢查 backend 目錄
if not exist "..\backend" (
    echo ❌ 錯誤：找不到 backend 目錄
    echo 請確保在正確的項目根目錄中運行
    pause
    exit /b 1
)

:: 檢查 Python 環境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：找不到 Python
    echo 請確保 Python 已安裝並在 PATH 中
    pause
    exit /b 1
)

:: 檢查 pytest
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：找不到 pytest
    echo 請安裝 pytest：pip install pytest
    pause
    exit /b 1
)

:menu
echo 請選擇測試類型：
echo.
echo 1. 🚀 快速測試 (單元測試)
echo 2. 🔍 完整測試 (所有測試)
echo 3. 📊 覆蓋率測試 (生成報告)
echo 4. 🎯 特定測試 (自定義)
echo 5. 🔧 修復測試 (修復失敗的測試)
echo 6. 📋 測試狀態 (查看測試結果)
echo 7. 🧹 清理測試 (清理測試數據)
echo 8. ❌ 退出
echo.

set /p choice="請輸入選項 (1-8): "

if "%choice%"=="1" goto quick_test
if "%choice%"=="2" goto full_test
if "%choice%"=="3" goto coverage_test
if "%choice%"=="4" goto custom_test
if "%choice%"=="5" goto fix_tests
if "%choice%"=="6" goto test_status
if "%choice%"=="7" goto cleanup_tests
if "%choice%"=="8" goto exit
goto invalid_choice

:quick_test
echo.
echo 🚀 執行快速測試...
echo ========================================
python -m pytest test_core_modules.py -v --tb=short -m "not slow"
if errorlevel 1 (
    echo.
    echo ❌ 快速測試失敗！
    echo 請檢查錯誤信息並修復問題
) else (
    echo.
    echo ✅ 快速測試通過！
)
goto end_test

:full_test
echo.
echo 🔍 執行完整測試...
echo ========================================
python -m pytest . -v --tb=short
if errorlevel 1 (
    echo.
    echo ❌ 完整測試失敗！
    echo 請檢查錯誤信息並修復問題
) else (
    echo.
    echo ✅ 完整測試通過！
)
goto end_test

:coverage_test
echo.
echo 📊 執行覆蓋率測試...
echo ========================================
python -m pytest . --cov=..\backend --cov-report=html --cov-report=term-missing -v
if errorlevel 1 (
    echo.
    echo ❌ 覆蓋率測試失敗！
) else (
    echo.
    echo ✅ 覆蓋率測試完成！
    echo 📁 報告位置：..\htmlcov\index.html
)
goto end_test

:custom_test
echo.
echo 🎯 自定義測試
echo ========================================
echo 可用的測試文件：
dir /b test_*.py
echo.
set /p test_file="請輸入測試文件名 (例如: test_core_modules.py): "
if "%test_file%"=="" goto menu

set /p test_class="請輸入測試類名 (可選，例如: TestConfigManagement): "
if "%test_class%"=="" (
    python -m pytest %test_file% -v --tb=short
) else (
    set /p test_method="請輸入測試方法名 (可選): "
    if "%test_method%"=="" (
        python -m pytest %test_file%::%test_class% -v --tb=short
    ) else (
        python -m pytest %test_file%::%test_class%::%test_method% -v --tb=short
    )
)
goto end_test

:fix_tests
echo.
echo 🔧 修復測試
echo ========================================
echo 正在檢查測試環境...
python -c "import backend.core.config" 2>nul
if errorlevel 1 (
    echo ❌ 無法導入 backend 模組
    echo 請檢查 Python 路徑設置
) else (
    echo ✅ backend 模組導入正常
)

echo.
echo 正在運行診斷測試...
python -m pytest test_core_modules.py::TestConfigManagement::test_settings_loading -v
if errorlevel 1 (
    echo ❌ 基礎配置測試失敗
    echo 請檢查 conftest.py 中的 mock 設置
) else (
    echo ✅ 基礎配置測試通過
)
goto end_test

:test_status
echo.
echo 📋 測試狀態
echo ========================================
echo 最後測試結果：
if exist "..\test_results.txt" (
    type "..\test_results.txt"
) else (
    echo 沒有找到測試結果文件
)
echo.
echo 測試覆蓋率：
if exist "..\htmlcov\index.html" (
    echo ✅ 覆蓋率報告已生成：..\htmlcov\index.html
) else (
    echo ❌ 沒有覆蓋率報告
)
goto end_test

:cleanup_tests
echo.
echo 🧹 清理測試數據
echo ========================================
echo 正在清理測試文件...

:: 清理測試數據目錄
if exist "test_data" (
    rmdir /s /q "test_data"
    echo ✅ 清理 test_data 目錄
)

if exist "test_vectors" (
    rmdir /s /q "test_vectors"
    echo ✅ 清理 test_vectors 目錄
)

:: 清理 pytest 緩存
if exist ".pytest_cache" (
    rmdir /s /q ".pytest_cache"
    echo ✅ 清理 pytest 緩存
)

:: 清理覆蓋率報告
if exist "..\htmlcov" (
    rmdir /s /q "..\htmlcov"
    echo ✅ 清理覆蓋率報告
)

echo.
echo ✅ 測試數據清理完成！
goto end_test

:invalid_choice
echo.
echo ❌ 無效選項，請重新選擇
goto menu

:end_test
echo.
echo ========================================
echo 測試完成！
echo ========================================
echo.
pause
goto menu

:exit
echo.
echo 👋 再見！
echo.
exit /b 0 