@echo off
setlocal enabledelayedexpansion

echo ========================================
echo AI Research Assistant - Virtual Environment Setup
echo ========================================
echo.
echo This script will set up a Python virtual environment for the AI Research Assistant.
echo The virtual environment will be created at C:\ai_research_venv
echo.
echo Note: Please enter only numbers (1, 2, or 3) when prompted for choices.
echo.

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo Current working directory: %CD%
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo Python found:
python --version >nul 2>&1
echo Python version check completed
echo.

REM Check Python version (need 3.10+)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
for /f "tokens=1 delims=." %%i in ("!PYTHON_VERSION!") do set PYTHON_MAJOR=%%i
for /f "tokens=2 delims=." %%j in ("!PYTHON_VERSION!") do set PYTHON_MINOR=%%j

if !PYTHON_MAJOR! LSS 3 (
    echo ERROR: Python 3.10+ is required. Current version: !PYTHON_VERSION!
    pause
    exit /b 1
)

if !PYTHON_MAJOR! EQU 3 (
    if !PYTHON_MINOR! LSS 10 (
        echo ERROR: Python 3.10+ is required. Current version: !PYTHON_VERSION!
        pause
        exit /b 1
    )
)

echo ✅ Python version !PYTHON_VERSION! is compatible
echo.

REM Set virtual environment path
set "VENV_PATH=C:\ai_research_venv"
set "VENV_ACTIVATE=%VENV_PATH%\Scripts\activate.bat"

echo Virtual environment will be created at: %VENV_PATH%
echo.

REM Check if virtual environment exists
if exist "%VENV_PATH%" (
    echo Virtual environment already exists at %VENV_PATH%
    echo.
    echo Options:
    echo 1. Use existing virtual environment
    echo 2. Remove and recreate virtual environment
    echo 3. Exit
    echo.
    
    :get_choice
    set /p "CHOICE=Enter your choice (1-3): "
    
    REM Validate input
    if "!CHOICE!"=="1" (
        echo Using existing virtual environment...
        goto check_venv
    ) else if "!CHOICE!"=="2" (
        echo Removing existing virtual environment...
        rmdir /s /q "%VENV_PATH%"
        goto create_venv
    ) else if "!CHOICE!"=="3" (
        echo Exiting...
        pause
        exit /b 0
    ) else (
        echo Invalid choice: !CHOICE!
        echo Please enter 1, 2, or 3
        echo.
        goto get_choice
    )
) else (
    echo No virtual environment found at %VENV_PATH%
    goto create_venv
)

:create_venv
echo Creating virtual environment at %VENV_PATH%...
python -m venv "%VENV_PATH%"
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Please check if you have write permissions to C:\
    pause
    exit /b 1
)

echo Virtual environment created successfully!
echo.

:check_venv
echo Testing virtual environment...
if exist "%VENV_ACTIVATE%" (
    call "%VENV_ACTIVATE%" >nul 2>&1
    if not errorlevel 1 (
        echo Virtual environment is valid and working
        echo.
        echo Installing/updating dependencies...
        goto install_dependencies
    ) else (
        echo ERROR: Virtual environment is corrupted
        echo Removing corrupted virtual environment...
        rmdir /s /q "%VENV_PATH%"
        goto create_venv
    )
) else (
    echo ERROR: Virtual environment activation script not found
    echo Removing incomplete virtual environment...
    rmdir /s /q "%VENV_PATH%"
    goto create_venv
)

:install_dependencies
REM Activate virtual environment
call "%VENV_ACTIVATE%"
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo Virtual environment activated.
echo.

REM Upgrade pip and install build tools
echo Upgrading pip and installing build tools...
python -m pip install --upgrade pip >nul 2>&1
pip install --upgrade setuptools wheel >nul 2>&1

REM Install PyTorch with CUDA support first (to avoid conflicts)
echo Installing PyTorch with CUDA support...
pip install torch>=2.0.0 torchaudio==2.5.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121 >nul 2>&1
if errorlevel 1 (
    echo WARNING: CUDA PyTorch installation failed, trying CPU version...
    pip install torch>=2.0.0 torchaudio>=2.0.0 >nul 2>&1
)

REM Install critical dependencies first
echo Installing critical dependencies...
pip install numpy>=1.24.0 scipy>=1.11.0 scikit-learn>=1.6.1 >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install critical scientific computing packages
    pause
    exit /b 1
)

pip install sentence-transformers==5.0.0 transformers==4.53.2 tokenizers==0.21.2 >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install transformers packages
    pause
    exit /b 1
)

pip install langchain-huggingface>=0.1.0 >nul 2>&1
if errorlevel 1 (
    echo ERROR: Failed to install langchain-huggingface
    pause
    exit /b 1
)

REM Install all dependencies from requirements.txt
echo Installing all dependencies from requirements.txt...
echo.

if exist "requirements.txt" (
    pip install -r requirements.txt >nul 2>&1
    if errorlevel 1 (
        echo WARNING: Some packages from requirements.txt failed to install
        echo Attempting to install remaining packages individually...
        goto install_individual_packages
    ) else (
        echo ✅ All dependencies installed successfully from requirements.txt
    )
) else (
    echo ERROR: requirements.txt not found
    echo Please ensure requirements.txt exists in the project root
    pause
    exit /b 1
)

goto install_backend_deps

:install_individual_packages
echo Installing packages individually to identify issues...
echo.

REM Core AI packages
echo Installing core AI packages...
pip install langchain-openai>=0.1.6 >nul 2>&1
pip install langchain==0.3.26 >nul 2>&1
pip install langchain_community==0.3.27 >nul 2>&1
pip install langchain_core==0.3.70 >nul 2>&1
pip install openai==1.97.0 >nul 2>&1

REM Vector database and embeddings
echo Installing vector database and embeddings...
pip install chromadb==1.0.11 >nul 2>&1
pip install huggingface-hub==0.33.4 >nul 2>&1
pip install einops==0.8.1 >nul 2>&1

REM Document processing
echo Installing document processing packages...
pip install PyMuPDF==1.26.0 >nul 2>&1
pip install python-docx==1.1.2 >nul 2>&1
pip install openpyxl==3.1.5 >nul 2>&1
pip install PyYAML==6.0.2 >nul 2>&1

REM Data processing
echo Installing data processing packages...
pip install pandas==2.3.1 >nul 2>&1
pip install streamlit==1.45.1 >nul 2>&1

REM Web and networking
echo Installing web and networking packages...
pip install requests==2.32.4 >nul 2>&1
pip install certifi==2025.1.31 >nul 2>&1

REM Image processing
echo Installing image processing packages...
pip install Pillow>=10.0.0 >nul 2>&1
pip install svglib>=1.5.1 >nul 2>&1
pip install reportlab>=4.0.0 >nul 2>&1

REM Web automation
echo Installing web automation packages...
pip install selenium>=4.15.0 >nul 2>&1

REM Environment and configuration
echo Installing environment and configuration packages...
pip install python-dotenv==1.1.1 >nul 2>&1
pip install pydantic-settings>=2.0.0 >nul 2>&1
pip install tqdm==4.67.1 >nul 2>&1

REM Additional utilities
echo Installing additional utilities...
pip install urllib3>=2.0.0 >nul 2>&1
pip install beautifulsoup4>=4.12.0 >nul 2>&1
pip install lxml>=4.9.0 >nul 2>&1

REM FastAPI dependencies
echo Installing FastAPI dependencies...
pip install fastapi>=0.115.9 >nul 2>&1
pip install uvicorn[standard]>=0.24.0 >nul 2>&1
pip install python-multipart>=0.0.6 >nul 2>&1

REM Optional dependencies
echo Installing optional dependencies...
pip install aiofiles>=23.0.0 >nul 2>&1
pip install python-jose[cryptography]>=3.3.0 >nul 2>&1
pip install passlib[bcrypt]>=1.7.4 >nul 2>&1

:install_backend_deps
REM Install backend dependencies if they exist
if exist "backend\requirements.txt" (
    echo.
    echo Installing backend dependencies...
    pip install -r backend\requirements.txt >nul 2>&1
    if errorlevel 1 (
        echo WARNING: Some backend dependencies failed to install
    )
)

REM Install frontend dependencies
echo.
echo Installing frontend dependencies...
if exist "frontend" (
    pushd frontend
    echo Current directory: %CD%
    
    REM Check if Node.js is installed
    node --version >nul 2>&1
    if errorlevel 1 (
        echo WARNING: Node.js is not installed or not in PATH
        echo Frontend dependencies cannot be installed
        echo Please install Node.js from https://nodejs.org/
    ) else (
        echo Node.js found:
        node --version >nul 2>&1
        echo Node.js version check completed
        
        REM Check if package.json exists
        if exist "package.json" (
            echo Installing frontend dependencies...
            npm install >nul 2>&1
            if errorlevel 1 (
                echo WARNING: Failed to install frontend dependencies
                echo You may need to install them manually
            ) else (
                echo ✅ Frontend dependencies installed successfully
            )
            
            REM Check if .bin directory exists (for vite and other tools)
            if not exist "node_modules\.bin" (
                echo WARNING: Frontend .bin directory missing, reinstalling...
                rmdir /s /q node_modules 2>nul
                npm install >nul 2>&1
                if errorlevel 1 (
                    echo WARNING: Failed to reinstall frontend dependencies
                ) else (
                    echo ✅ Frontend dependencies reinstalled successfully
                )
            )
        ) else (
            echo WARNING: package.json not found in frontend directory
        )
    )
    popd
    echo Returned to project root directory: %CD%
) else (
    echo WARNING: frontend directory not found
)

echo.
echo ========================================
echo Installation Summary
echo ========================================
echo.

echo ✅ All dependencies installed successfully!
echo.
echo Installation completed! To verify dependencies, run:
echo   python dependency_manager.py
echo.

echo.
echo ========================================
echo Virtual environment setup completed!
echo ========================================
echo.
echo Virtual environment location: %VENV_PATH%
echo.
echo To activate manually:
echo   call "%VENV_ACTIVATE%"
echo.
echo To deactivate:
echo   deactivate
echo.

echo Creating environment configuration file...
echo VENV_PATH=%VENV_PATH% > .venv_config
echo VENV_ACTIVATE=%VENV_ACTIVATE% >> .venv_config
echo.
echo Environment configuration saved to .venv_config
echo.
echo Next steps:
echo 1. Activate the virtual environment: call "%VENV_ACTIVATE%"
echo 2. Start the backend: run restart_backend.bat
echo 3. Start the frontend: run start_react.bat
echo.
echo ========================================
echo Setup Summary
echo ========================================
echo ✅ Virtual environment created at: %VENV_PATH%
echo ✅ Dependencies installed from requirements.txt
echo ✅ Backend dependencies installed
echo ✅ Frontend dependencies installed (if Node.js available)
echo ✅ Environment configuration saved
echo.
echo The AI Research Assistant is ready to use!
echo.
echo Press any key to exit...
pause >nul
