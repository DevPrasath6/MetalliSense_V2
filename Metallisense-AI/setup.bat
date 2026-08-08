@echo off
REM MetalliSense AI Service - Windows Setup Script

echo ========================================
echo MetalliSense AI Service Setup
echo ========================================
echo.

REM Check Python 3.11 installation using Python Launcher
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11 is required but not found!
    echo.
    echo Please install Python 3.11 from:
    echo https://www.python.org/downloads/release/python-3119/
    echo.
    echo Note: Make sure to check "Install launcher for all users" during installation
    echo.
    pause
    exit /b 1
)

echo Found Python 3.11
py -3.11 --version

echo.
echo [1/5] Creating virtual environment with Python 3.11...
if not exist "venv" (
    py -3.11 -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)

echo.
echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo [3/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [4/5] Setting up directories...
if not exist "app\data" mkdir app\data
if not exist "app\models" mkdir app\models

echo.
echo [5/5] Running complete setup (data generation + training)...
python setup.py
if errorlevel 1 (
    echo ERROR: Setup failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo.
echo IMPORTANT: Always activate virtual environment first!
echo    venv\Scripts\activate
echo.
echo 1. Start the API service:
echo    python app\main.py
echo.
echo 2. Test the API (in another terminal):
echo    python test_api.py
echo.
echo 3. Access documentation:
echo    http://localhost:8000/docs
echo.
echo To deactivate virtual environment:
echo    deactivate
echo ========================================
echo.
pause
