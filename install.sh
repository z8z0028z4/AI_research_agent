#!/bin/bash

echo "========================================"
echo "AI Research Assistant - Installation"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.10 or 3.11 from https://python.org"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python version: $python_version"

# Check if version is 3.10 or higher
if [[ $(echo "$python_version >= 3.10" | bc -l) -eq 0 ]]; then
    echo "ERROR: Python 3.10 or higher is required"
    echo "Current version: $python_version"
    exit 1
fi

echo
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

echo
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

echo
echo "Upgrading pip..."
python -m pip install --upgrade pip

echo
echo "Installing dependencies..."
pip install -r research_agent/requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    echo "Please check your internet connection and try again"
    exit 1
fi

echo
echo "Setting up environment file..."
if [ ! -f "research_agent/.env" ]; then
    cp research_agent/env.example research_agent/.env
    echo
    echo "IMPORTANT: Please edit research_agent/.env and add your API keys:"
    echo "- OPENAI_API_KEY: Get from https://platform.openai.com/api-keys"
    echo "- PERPLEXITY_API_KEY: Get from https://www.perplexity.ai/settings/api"
    echo
else
    echo "Environment file already exists"
fi

echo
echo "========================================"
echo "Installation completed successfully!"
echo "========================================"
echo
echo "To start the application:"
echo "1. cd research_agent"
echo "2. python app/main.py"
echo
echo "Or activate the virtual environment and run:"
echo "source venv/bin/activate"
echo "cd research_agent"
echo "python app/main.py"
echo 