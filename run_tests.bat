@echo off
chcp 65001 >nul 2>&1

echo.
echo 🧪 AI Research Assistant - Unified Test Entry
echo ===============================
echo.

:: If there is a parameter, run the corresponding test directly
if not "%1"=="" (
    call :run_test_by_param %1
    goto :end
)

:: Show menu
:show_menu
echo Please select a test type:
echo.
echo [1] Quick Test - Core Functions
echo [2] Full Test - All Functions
echo [3] Coverage Test
echo [4] API Test
echo [5] End-to-End Test
echo [6] Proposal Feature E2E Test
echo [7] Service Layer Test
echo [8] Core Module Test
echo [9] Utility Test
echo [10] Frontend Test
echo [0] Check Dependencies
echo.
set /p choice="Enter option number (1-10, 0): "

:: Run the corresponding test based on selection
if "%choice%"=="1" (
    echo Quick Test - Core Functions
    python tests\run_tests.py --type quick
    goto :end
)
if "%choice%"=="2" (
    echo Full Test - All Functions
    python tests\run_tests.py --type all
    goto :end
)
if "%choice%"=="3" (
    echo Coverage Test
    python tests\run_tests.py --type coverage
    goto :end
)
if "%choice%"=="4" (
    echo API Test
    python tests\run_tests.py --type api
    goto :end
)
if "%choice%"=="5" (
    echo End-to-End Test
    python tests\run_tests.py --type e2e
    goto :end
)
if "%choice%"=="6" (
    echo Proposal Feature E2E Test
    python tests\run_tests.py --type proposal
    goto :end
)
if "%choice%"=="7" (
    echo Service Layer Test
    python tests\run_tests.py --type services
    goto :end
)
if "%choice%"=="8" (
    echo Core Module Test
    python tests\run_tests.py --type core
    goto :end
)
if "%choice%"=="9" (
    echo Utility Test
    python tests\run_tests.py --type utils
    goto :end
)
if "%choice%"=="10" (
    echo Frontend Test
    python tests\run_tests.py --type frontend
    goto :end
)
if "%choice%"=="0" (
    echo Check Dependencies
    python tests\run_tests.py --check-deps
    goto :end
)

echo ❌ Invalid option, please select again.
echo.
goto :show_menu

:: Function to handle command line parameters
:run_test_by_param
if "%1"=="all" (
    echo Full Test - All Functions
    python tests\run_tests.py --type all
    exit /b
)
if "%1"=="coverage" (
    echo Coverage Test
    python tests\run_tests.py --type coverage
    exit /b
)
if "%1"=="api" (
    echo API Test
    python tests\run_tests.py --type api
    exit /b
)
if "%1"=="e2e" (
    echo End-to-End Test
    python tests\run_tests.py --type e2e
    exit /b
)
if "%1"=="deps" (
    echo Check Dependencies
    python tests\run_tests.py --check-deps
    exit /b
)
if "%1"=="services" (
    echo Service Layer Test
    python tests\run_tests.py --type services
    exit /b
)
if "%1"=="core" (
    echo Core Module Test
    python tests\run_tests.py --type core
    exit /b
)
if "%1"=="utils" (
    echo Utility Test
    python tests\run_tests.py --type utils
    exit /b
)
if "%1"=="frontend" (
    echo Frontend Test
    python tests\run_tests.py --type frontend
    exit /b
)
:: Default: run quick test
echo Quick Test - Core Functions
python tests\run_tests.py --type quick
exit /b

:end
echo.
if errorlevel 1 (
    echo ❌ Test Failed!
) else (
    echo ✅ Test Completed!
)
pause