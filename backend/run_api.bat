@echo off
setlocal enabledelayedexpansion

echo Starting AI Research Assistant Backend API...
cd /d "%~dp0"

REM Get the parent directory (project root)
set "PROJECT_ROOT=%~dp0.."

echo Current directory: %CD%
echo Project root: %PROJECT_ROOT%
echo.

REM Load virtual environment configuration
set "VENV_PATH="
set "VENV_ACTIVATE="

if exist "%PROJECT_ROOT%\.venv_config" (
    for /f "tokens=1,2 delims==" %%a in (%PROJECT_ROOT%\.venv_config) do (
        if "%%a"=="VENV_PATH" set "VENV_PATH=%%b"
        if "%%a"=="VENV_ACTIVATE" set "VENV_ACTIVATE=%%b"
    )
)

REM Check if virtual environment is configured
if not defined VENV_PATH (
    echo ERROR: Virtual environment not configured
    echo Please run venv_setup.bat from the project root first
    pause
    exit /b 1
)

echo Virtual environment path: %VENV_PATH%
echo.

REM Check if virtual environment exists
if not exist "%VENV_PATH%" (
    echo ERROR: Virtual environment not found at %VENV_PATH%
    echo Please run venv_setup.bat to create the virtual environment
    pause
    exit /b 1
)

REM Check if activation script exists
if not exist "%VENV_ACTIVATE%" (
    echo ERROR: Virtual environment activation script not found
    echo Please run venv_setup.bat to recreate the virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_ACTIVATE%"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Please run venv_setup.bat to fix the virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated successfully.
echo.

REM Check dependencies before starting
echo Checking dependencies...
cd /d "%PROJECT_ROOT%"
python check_deps.py

if errorlevel 1 (
    echo WARNING: Some dependencies are missing
    echo Please run venv_setup.bat to install dependencies
    echo.
    echo Continue anyway? (Y/N)
    
    :get_continue_choice
    set /p "CONTINUE_CHOICE="
    
    REM Validate input
    if /i "!CONTINUE_CHOICE!"=="Y" (
        echo Continuing with missing dependencies...
    ) else if /i "!CONTINUE_CHOICE!"=="N" (
        echo Exiting...
        pause
        exit /b 1
    ) else (
        echo Invalid choice: !CONTINUE_CHOICE!
        echo Please enter Y or N
        echo.
        goto get_continue_choice
    )
)

REM Return to backend directory
cd /d "%~dp0"

REM Check if main.py exists
if not exist "main.py" (
    echo ERROR: main.py not found
    echo Please ensure you're running this from the backend directory
    pause
    exit /b 1
)

REM Start the FastAPI server
echo.
echo Starting FastAPI server on http://localhost:8000
echo API documentation available at http://localhost:8000/api/docs
echo Press Ctrl+C to stop the server
echo.

python main.py

echo.
echo Server stopped.
pause 