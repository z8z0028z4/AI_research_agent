@echo off
echo 🧪 AI Research Agent Test Runner
echo ================================

if "%1"=="" (
    echo Running all tests...
    cd tests
    python run_tests.py all
) else (
    echo Running %1 tests...
    cd tests
    python run_tests.py %1
)

echo.
echo Tests completed!
pause 