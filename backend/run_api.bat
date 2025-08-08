@echo off
echo Starting AI Research Assistant Backend API...
cd /d "%~dp0"

REM Check if virtual environment exists
if exist "..\venv\Scripts\activate.bat" (
    echo Using venv virtual environment...
    call ..\venv\Scripts\activate.bat
) else if exist "..\venv_company\Scripts\activate.bat" (
    echo Using venv_company virtual environment...
    call ..\venv_company\Scripts\activate.bat
) else (
    echo Error: Virtual environment not found
    echo Please run install.bat first to install dependencies
    pause
    exit /b 1
)

REM Install backend dependencies if needed
if not exist "requirements.txt" (
    echo Error: requirements.txt not found
    pause
    exit /b 1
)

echo Installing backend dependencies...
pip install -r requirements.txt

REM Start the FastAPI server
echo Starting FastAPI server on http://localhost:8000
echo API documentation available at http://localhost:8000/api/docs
python main.py

pause 