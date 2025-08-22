@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo 🚀 AI Research Agent 快速測試
echo ========================================
echo.

:: 檢查環境
if not exist "test_core_modules.py" (
    echo ❌ 錯誤：請在 tests/ 目錄中運行此腳本
    pause
    exit /b 1
)

echo 🔍 檢查測試環境...
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：找不到 pytest
    echo 請安裝：pip install pytest
    pause
    exit /b 1
)

echo ✅ 環境檢查完成
echo.

echo 🚀 開始快速測試...
echo ========================================

:: 運行核心模組測試
echo 📋 測試核心模組...
python -m pytest test_core_modules.py::TestConfigManagement -v --tb=short
if errorlevel 1 (
    echo ❌ 配置管理測試失敗
    goto test_failed
)

echo ✅ 配置管理測試通過

:: 測試 LLM 管理器
echo 📋 測試 LLM 管理器...
python -m pytest test_core_modules.py::TestLLMManager -v --tb=short
if errorlevel 1 (
    echo ❌ LLM 管理器測試失敗
    goto test_failed
)

echo ✅ LLM 管理器測試通過

:: 測試生成模組
echo 📋 測試生成模組...
python -m pytest test_core_modules.py::TestGeneration -v --tb=short
if errorlevel 1 (
    echo ❌ 生成模組測試失敗
    goto test_failed
)

echo ✅ 生成模組測試通過

:: 測試向量存儲
echo 📋 測試向量存儲...
python -m pytest test_core_modules.py::TestVectorStore -v --tb=short
if errorlevel 1 (
    echo ❌ 向量存儲測試失敗
    goto test_failed
)

echo ✅ 向量存儲測試通過

:: 測試檢索功能
echo 📋 測試檢索功能...
python -m pytest test_core_modules.py::TestRetrieval -v --tb=short
if errorlevel 1 (
    echo ❌ 檢索功能測試失敗
    goto test_failed
)

echo ✅ 檢索功能測試通過

:: 測試提示詞構建
echo 📋 測試提示詞構建...
python -m pytest test_core_modules.py::TestPromptBuilder -v --tb=short
if errorlevel 1 (
    echo ❌ 提示詞構建測試失敗
    goto test_failed
)

echo ✅ 提示詞構建測試通過

:: 測試 Schema 管理
echo 📋 測試 Schema 管理...
python -m pytest test_core_modules.py::TestSchemaManager -v --tb=short
if errorlevel 1 (
    echo ❌ Schema 管理測試失敗
    goto test_failed
)

echo ✅ Schema 管理測試通過

echo.
echo ========================================
echo ✅ 快速測試全部通過！
echo ========================================
echo.
echo 🎉 核心功能測試成功
echo 📊 所有基礎模組運行正常
echo 🔧 可以繼續開發新功能
echo.
goto end

:test_failed
echo.
echo ========================================
echo ❌ 快速測試失敗！
echo ========================================
echo.
echo 🔧 建議修復步驟：
echo 1. 檢查 conftest.py 中的 mock 設置
echo 2. 確認 backend 模組導入正常
echo 3. 檢查測試依賴是否完整
echo 4. 運行完整測試查看詳細錯誤
echo.
echo 💡 提示：使用 run_tests.bat 的"修復測試"選項
echo.

:end
pause 