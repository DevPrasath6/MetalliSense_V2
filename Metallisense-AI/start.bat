

@echo off
REM Quick start script for MetalliSense AI Service (Windows)

echo ========================================
echo Starting MetalliSense AI Service
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run setup.bat first
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting API service on http://localhost:8000
echo Press Ctrl+C to stop the service
echo.
echo API Documentation: http://localhost:8000/docs
echo ========================================
echo.

python app\main.py
