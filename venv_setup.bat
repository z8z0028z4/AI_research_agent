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
python --version
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

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install wheel and setuptools first
echo Installing build tools...
pip install wheel setuptools

REM Install PyTorch with CUDA support first (to avoid conflicts)
echo Installing PyTorch with CUDA support...
pip install torch>=2.0.0 torchaudio==2.5.1+cu121 --extra-index-url https://download.pytorch.org/whl/cu121
if errorlevel 1 (
    echo WARNING: CUDA PyTorch installation failed, trying CPU version...
    pip install torch>=2.0.0 torchaudio>=2.0.0
)

REM Install critical dependencies first
echo Installing critical dependencies...
pip install numpy>=1.24.0 scipy>=1.11.0 scikit-learn>=1.6.1
pip install sentence-transformers==5.0.0 transformers==4.53.2 tokenizers==0.21.2
pip install langchain-huggingface>=0.1.0

REM Install all dependencies from requirements.txt
echo Installing all dependencies from requirements.txt...
echo.

if exist "requirements.txt" (
    pip install -r requirements.txt
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
pip install langchain-openai>=0.1.6
pip install langchain==0.3.26
pip install langchain_community==0.3.27
pip install langchain_core==0.3.70
pip install openai==1.97.0
pip install chromadb==1.0.11
pip install huggingface-hub==0.33.4
pip install einops==0.8.1
pip install PyMuPDF==1.26.0
pip install python-docx==1.1.2
pip install openpyxl==3.1.5
pip install PyYAML==6.0.2
pip install pandas==2.3.1
pip install streamlit==1.45.1
pip install requests==2.32.4
pip install certifi==2025.1.31
pip install Pillow>=10.0.0
pip install svglib>=1.5.1
pip install reportlab>=4.0.0
pip install selenium>=4.15.0
pip install python-dotenv==1.1.1
pip install pydantic-settings>=2.0.0
pip install tqdm==4.67.1
pip install urllib3>=2.0.0
pip install beautifulsoup4>=4.12.0
pip install lxml>=4.9.0

:install_backend_deps
REM Install backend dependencies if they exist
if exist "backend\requirements.txt" (
    echo.
    echo Installing backend dependencies...
    pip install -r backend\requirements.txt
    if errorlevel 1 (
        echo WARNING: Some backend dependencies failed to install
    )
)

echo.
echo ========================================
echo Dependency Installation Summary
echo ========================================
echo.

REM Check critical dependencies
echo Checking critical dependencies...
python check_deps.py

if errorlevel 1 (
    echo.
    echo WARNING: Some dependencies are missing
    echo Running dependency fix script...
    echo.
    
    if exist "fix_deps.py" (
        python fix_deps.py
        
        echo.
        echo Re-checking dependencies...
        python check_deps.py
        if errorlevel 1 (
            echo.
            echo WARNING: Some dependencies are still missing
            echo You may need to install them manually or check your internet connection
        ) else (
            echo.
            echo ✅ All dependencies are now available!
        )
    ) else (
        echo.
        echo fix_deps.py not found, attempting manual installation of missing packages...
        pip install sentence-transformers==5.0.0 --force-reinstall
        pip install langchain-huggingface>=0.1.0
    )
) else (
    echo.
    echo ✅ All dependencies installed successfully!
)

REM Check PyTorch CUDA status
echo.
echo Checking PyTorch CUDA status...
if exist "check_cuda.py" (
    python check_cuda.py
) else (
    echo check_cuda.py not found, skipping CUDA check
)

REM Test critical imports
echo.
echo Testing critical imports...
python -c "import sentence_transformers; print('✅ sentence-transformers imported successfully')" 2>nul
if errorlevel 1 (
    echo ❌ sentence-transformers import failed
    echo Attempting to reinstall...
    pip install sentence-transformers==5.0.0 --force-reinstall
)

python -c "import langchain_huggingface; print('✅ langchain-huggingface imported successfully')" 2>nul
if errorlevel 1 (
    echo ❌ langchain-huggingface import failed
    echo Attempting to reinstall...
    pip install langchain-huggingface>=0.1.0 --force-reinstall
)

REM Check optional dependencies for DOCX generation
echo.
echo Checking optional dependencies for DOCX generation...
python -c "from svglib.svglib import svg2rlg; from reportlab.graphics import renderPDF; print('✅ svglib and reportlab available for SVG processing')" 2>nul
if errorlevel 1 (
    echo ⚠️ svglib or reportlab not available - SVG processing will be disabled
    echo To enable SVG processing, install: pip install svglib reportlab
)

python -c "import fitz; print('✅ PyMuPDF available for PDF processing')" 2>nul
if errorlevel 1 (
    echo ⚠️ PyMuPDF not available - PDF processing will be disabled
    echo To enable PDF processing, install: pip install PyMuPDF
)

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
pause
