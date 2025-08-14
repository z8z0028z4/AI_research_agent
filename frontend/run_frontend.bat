@echo off
setlocal enabledelayedexpansion

echo Starting AI Research Assistant Frontend...
cd /d "%~dp0"

echo Current directory: %CD%
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    echo Make sure to check "Add to PATH" during installation
    pause
    exit /b 1
)

echo Node.js version:
node --version
echo.

REM Check if package.json exists
if not exist "package.json" (
    echo ERROR: package.json not found
    echo Current directory: %CD%
    echo Please ensure you're running this from the frontend directory
    pause
    exit /b 1
)

REM Check if node_modules exists, if not install dependencies
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )
) else (
    echo Dependencies already installed
)

REM Check if vite.config.js exists (for Vite projects)
if exist "vite.config.js" (
    echo Vite project detected
) else if exist "webpack.config.js" (
    echo Webpack project detected
) else (
    echo WARNING: No build configuration found
    echo This might be a simple HTML project
)

echo.
echo Starting development server on http://localhost:3000
echo Press Ctrl+C to stop the server
echo.

REM Start the development server
npm run dev

echo.
echo Development server stopped.
pause 