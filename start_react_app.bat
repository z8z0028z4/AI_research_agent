@echo off
echo Starting AI Research Assistant (React Version)...
echo ================================================

REM Check if backend and frontend directories exist
if not exist "backend" (
    echo Error: Backend directory not found
    pause
    exit /b 1
)

if not exist "frontend" (
    echo Error: Frontend directory not found
    pause
    exit /b 1
)

echo.
echo Starting Backend API Server...
echo Backend will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/api/docs
echo.

REM Start backend in a new window
start "AI Research Assistant Backend" cmd /k "cd backend && run_api.bat"

echo.
echo Starting Frontend Development Server...
echo Frontend will be available at: http://localhost:3000
echo.

REM Start frontend in a new window
start "AI Research Assistant Frontend" cmd /k "cd frontend && run_frontend.bat"

echo.
echo Both services are starting...
echo Please wait a moment for the services to fully start.
echo.
echo Backend API: http://localhost:8000
echo Frontend App: http://localhost:3000
echo API Docs: http://localhost:8000/api/docs
echo.

pause 