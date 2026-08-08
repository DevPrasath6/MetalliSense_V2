#!/bin/bash
# MetalliSense AI Service - Linux/Mac Setup Script

echo "========================================"
echo "MetalliSense AI Service Setup"
echo "========================================"
echo ""

# Check Python 3.11 installation
if ! command -v python3.11 &> /dev/null; then
    echo "ERROR: Python 3.11 is required but not found!"
    echo ""
    echo "Please install Python 3.11:"
    echo "  Ubuntu/Debian: sudo apt install python3.11 python3.11-venv"
    echo "  macOS: brew install python@3.11"
    echo "  Or download from: https://www.python.org/downloads/"
    echo ""
    exit 1
fi

echo "Found Python 3.11"
python3.11 --version

echo ""
echo "[1/5] Creating virtual environment with Python 3.11..."
if [ ! -d "venv" ]; then
    python3.11 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully"
else
    echo "Virtual environment already exists"
fi

echo ""
echo "[2/5] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

echo ""
echo "[3/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[4/5] Setting up directories..."
mkdir -p app/data
mkdir -p app/models

echo ""
echo "[5/5] Running complete setup (data generation + training)..."
python setup.py
if [ $? -ne 0 ]; then
    echo "ERROR: Setup failed"
    exit 1
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "========================================"
echo "Next Steps:"
echo "========================================"
echo ""
echo "IMPORTANT: Always activate virtual environment first!"
echo "   source venv/bin/activate"
echo ""
echo "1. Start the API service:"
echo "   python app/main.py"
echo ""
echo "2. Test the API (in another terminal):"
echo "   python test_api.py"
echo ""
echo "3. Access documentation:"
echo "   http://localhost:8000/docs"
echo ""
echo "To deactivate virtual environment:"
echo "   deactivate"
echo "========================================"
echo ""
