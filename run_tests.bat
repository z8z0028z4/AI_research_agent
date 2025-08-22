@echo off
chcp 65001 >nul 2>&1

echo.
echo 🧪 AI研究助理 - 統一測試入口
echo ===============================
echo.

:: 如果有參數，直接執行對應的測試
if not "%1"=="" (
    call :run_test_by_param %1
    goto :end
)

:: 顯示選單
:show_menu
echo 請選擇測試類型：
echo.
echo [1] 快速測試 - 核心功能
echo [2] 完整測試 - 所有功能
echo [3] 覆蓋率測試
echo [4] API測試
echo [5] 端到端測試
echo [6] 服務測試
echo [7] 核心測試
echo [8] 工具測試
echo [9] 前端測試
echo [0] 檢查依賴
echo.
set /p choice="請輸入選項數字 (1-9, 0): "

:: 根據選擇執行對應測試
if "%choice%"=="1" (
    echo 快速測試 - 核心功能
    python tests\run_tests.py --type quick
    goto :end
)
if "%choice%"=="2" (
    echo 完整測試 - 所有功能
    python tests\run_tests.py --type all
    goto :end
)
if "%choice%"=="3" (
    echo 覆蓋率測試
    python tests\run_tests.py --type coverage
    goto :end
)
if "%choice%"=="4" (
    echo API測試
    python tests\run_tests.py --type api
    goto :end
)
if "%choice%"=="5" (
    echo 端到端測試
    python tests\run_tests.py --type e2e
    goto :end
)
if "%choice%"=="6" (
    echo 服務測試
    python tests\run_tests.py --type services
    goto :end
)
if "%choice%"=="7" (
    echo 核心測試
    python tests\run_tests.py --type core
    goto :end
)
if "%choice%"=="8" (
    echo 工具測試
    python tests\run_tests.py --type utils
    goto :end
)
if "%choice%"=="9" (
    echo 前端測試
    python tests\run_tests.py --type frontend
    goto :end
)
if "%choice%"=="0" (
    echo 檢查依賴
    python tests\run_tests.py --check-deps
    goto :end
)

echo ❌ 無效的選項，請重新選擇
echo.
goto :show_menu

:: 處理命令行參數的函數
:run_test_by_param
if "%1"=="all" (
    echo 完整測試 - 所有功能
    python tests\run_tests.py --type all
    exit /b
)
if "%1"=="coverage" (
    echo 覆蓋率測試
    python tests\run_tests.py --type coverage
    exit /b
)
if "%1"=="api" (
    echo API測試
    python tests\run_tests.py --type api
    exit /b
)
if "%1"=="e2e" (
    echo 端到端測試
    python tests\run_tests.py --type e2e
    exit /b
)
if "%1"=="deps" (
    echo 檢查依賴
    python tests\run_tests.py --check-deps
    exit /b
)
if "%1"=="services" (
    echo 服務測試
    python tests\run_tests.py --type services
    exit /b
)
if "%1"=="core" (
    echo 核心測試
    python tests\run_tests.py --type core
    exit /b
)
if "%1"=="utils" (
    echo 工具測試
    python tests\run_tests.py --type utils
    exit /b
)
if "%1"=="frontend" (
    echo 前端測試
    python tests\run_tests.py --type frontend
    exit /b
)
:: 預設執行快速測試
echo 快速測試 - 核心功能
python tests\run_tests.py --type quick
exit /b

:end
echo.
if errorlevel 1 (
    echo ❌ 測試失敗！
) else (
    echo ✅ 測試完成！
)
pause