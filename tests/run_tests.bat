@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo 🧪 AI Research Agent Test Suite
echo ========================================
echo.

:: Check if in the correct directory
if not exist "test_core_modules.py" (
    echo ❌ Error: Please run this script in the tests/ directory
    echo Current directory: %CD%
    echo Please run: cd tests
    pause
    exit /b 1
)

:: Check for backend directory
if not exist "..\backend" (
    echo ❌ Error: backend directory not found
    echo Please make sure you are running in the correct project root
    pause
    exit /b 1
)

:: Check Python environment
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python not found
    echo Please make sure Python is installed and in your PATH
    pause
    exit /b 1
)

:: Check pytest
python -c "import pytest" >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: pytest not found
    echo Please install pytest: pip install pytest
    pause
    exit /b 1
)

:menu
echo Please select a test type:
echo.
echo 1. 🚀 Quick Check (Environment & Fast Tests)
echo 2. 🔍 Full Test (All Tests)
echo 3. 📊 Coverage Test (Generate Report)
echo 4. 🎯 Custom Test (Specify)
echo 5. 🔧 Fix Tests (Repair Failed Tests)
echo 6. 📋 Test Status (View Results)
echo 7. 🧹 Clean Up Tests (Remove Test Data)
echo 8. 👀 Watch Mode (Auto-test on file changes)
echo 9. ❌ Exit
echo.

set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto quick_check
if "%choice%"=="2" goto full_test
if "%choice%"=="3" goto coverage_test
if "%choice%"=="4" goto custom_test
if "%choice%"=="5" goto fix_tests
if "%choice%"=="6" goto test_status
if "%choice%"=="7" goto cleanup_tests
if "%choice%"=="8" goto watch_mode
if "%choice%"=="9" goto exit
goto invalid_choice

:quick_check
echo.
echo 🚀 Running Quick Check...
echo ========================================
python test_quick_check.py
if errorlevel 1 (
    echo.
    echo ❌ Quick Check Failed!
    echo Please fix the issues before continuing
) else (
    echo.
    echo ✅ Quick Check Passed!
    echo You can now proceed with development
)
goto end_test

:full_test
echo.
echo 🔍 Running Full Test...
echo ========================================
python -m pytest . -v --tb=short
if errorlevel 1 (
    echo.
    echo ❌ Full Test Failed!
    echo Please check the error messages and fix the issues
) else (
    echo.
    echo ✅ Full Test Passed!
)
goto end_test

:coverage_test
echo.
echo 📊 Running Coverage Test...
echo ========================================
python -m pytest . --cov=..\backend --cov-report=html --cov-report=term-missing -v
if errorlevel 1 (
    echo.
    echo ❌ Coverage Test Failed!
) else (
    echo.
    echo ✅ Coverage Test Completed!
    echo 📁 Report location: ..\htmlcov\index.html
)
goto end_test

:custom_test
echo.
echo 🎯 Custom Test
echo ========================================
echo Available test files:
dir /b test_*.py
echo.
set /p test_file="Enter test file name (e.g., test_core_modules.py): "
if "%test_file%"=="" goto menu

set /p test_class="Enter test class name (optional, e.g., TestConfigManagement): "
if "%test_class%"=="" (
    python -m pytest %test_file% -v --tb=short
) else (
    set /p test_method="Enter test method name (optional): "
    if "%test_method%"=="" (
        python -m pytest %test_file%::%test_class% -v --tb=short
    ) else (
        python -m pytest %test_file%::%test_class%::%test_method% -v --tb=short
    )
)
goto end_test

:fix_tests
echo.
echo 🔧 Fix Tests
echo ========================================
echo Checking test environment...
python -c "import backend.core.config" 2>nul
if errorlevel 1 (
    echo ❌ Unable to import backend module
    echo Please check your Python path settings
) else (
    echo ✅ backend module imported successfully
)

echo.
echo Running diagnostic test...
python -m pytest test_core_modules.py::TestConfigManagement::test_settings_loading -v
if errorlevel 1 (
    echo ❌ Basic config test failed
    echo Please check mock settings in conftest.py
) else (
    echo ✅ Basic config test passed
)
goto end_test

:test_status
echo.
echo 📋 Test Status
echo ========================================
echo Last test results:
if exist "..\test_results.txt" (
    type "..\test_results.txt"
) else (
    echo No test results file found
)
echo.
echo Test coverage:
if exist "..\htmlcov\index.html" (
    echo ✅ Coverage report generated: ..\htmlcov\index.html
) else (
    echo ❌ No coverage report found
)
goto end_test

:cleanup_tests
echo.
echo 🧹 Cleaning Up Test Data
echo ========================================
echo Removing test files...

:: Remove test data directory
if exist "test_data" (
    rmdir /s /q "test_data"
    echo ✅ test_data directory cleaned
)

if exist "test_vectors" (
    rmdir /s /q "test_vectors"
    echo ✅ test_vectors directory cleaned
)

:: Remove pytest cache
if exist ".pytest_cache" (
    rmdir /s /q ".pytest_cache"
    echo ✅ pytest cache cleaned
)

:: Remove coverage report
if exist "..\htmlcov" (
    rmdir /s /q "..\htmlcov"
    echo ✅ coverage report cleaned
)

echo.
echo ✅ Test data cleanup completed!
goto end_test

:watch_mode
echo.
echo 👀 Starting Watch Mode...
echo ========================================
echo This will automatically run tests when files change
echo Press Ctrl+C to stop watching
echo.
echo Options:
echo 1. Fast tests only (recommended for development)
echo 2. Full tests with coverage
echo 3. Custom watch settings
echo.
set /p watch_choice="Enter your choice (1-3): "

if "%watch_choice%"=="1" (
    echo Starting fast test watch mode...
    python test_watch.py --fast
) else if "%watch_choice%"=="2" (
    echo Starting full test watch mode...
    python test_watch.py --coverage
) else if "%watch_choice%"=="3" (
    echo Starting custom watch mode...
    python test_watch.py
) else (
    echo Invalid choice, using default settings...
    python test_watch.py --fast
)
goto end_test

:invalid_choice
echo.
echo ❌ Invalid option, please select again
goto menu

:end_test
echo.
echo ========================================
echo Test Finished!
echo ========================================
echo.
echo 💡 Tips for effective testing:
echo   - Use Quick Check before starting development
echo   - Use Watch Mode during active development
echo   - Run Full Test before committing changes
echo   - Check coverage regularly to ensure good test coverage
echo.
pause
goto menu

:exit
echo.
echo 👋 Goodbye!
echo.
exit /b 0 