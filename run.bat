@echo off
echo Starting AI Research Assistant...
cd /d "%~dp0"

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Using venv virtual environment...
    call venv\Scripts\activate.bat
) else if exist "venv_company\Scripts\activate.bat" (
    echo Using venv_company virtual environment...
    call venv_company\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found
    echo Please run install.bat first to install dependencies
    pause
    exit /b 1
)

REM Check if run_from_root.py exists
if exist "run_from_root.py" (
    echo Starting with run_from_root.py...
    python run_from_root.py
) else if exist "app\main.py" (
    echo Starting with app\main.py...
    python app\main.py
) else (
    echo Error: Startup file not found
    echo Please check if run_from_root.py or app\main.py exists
    pause
    exit /b 1
)

pause