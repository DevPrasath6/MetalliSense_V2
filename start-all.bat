@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo   MetalliSense - Full Stack Launcher
echo ============================================================
echo.
echo This sets up (if needed) and starts:
echo   1. Metallisense-Agent    (Python AI service    - port 8001)
echo   2. MetalliSense-Node-BE  (Node.js backend       - port 3000)
echo   3. Metallisense-frontend (React/Vite frontend   - port 5173)
echo.
echo Note: Metallisense-AI is a legacy module (superseded by
echo       Metallisense-Agent) and is intentionally not started here.
echo ============================================================
echo.

set "ROOT=%~dp0"

where node >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found on PATH. Install it from https://nodejs.org/
    pause
    exit /b 1
)

if not exist "%ROOT%Metallisense-Agent" (
    echo ERROR: This script must stay in the repository root - Metallisense-Agent not found next to it.
    pause
    exit /b 1
)

REM ============================================================
REM 1) Metallisense-Agent - Python AI service (needs a venv)
REM ============================================================
echo [1/3] Preparing Metallisense-Agent...
cd /d "%ROOT%Metallisense-Agent"

if not exist ".env" if exist ".env.example" (
    copy /Y ".env.example" ".env" >nul
    echo   Created .env from .env.example - add your real GROQ_API_KEY before relying on copilot features.
)

if not exist "venv\Scripts\activate.bat" (
    echo   No virtual environment found - running setup.bat ^(creates venv, installs deps, trains models^)...
    call setup.bat
    if errorlevel 1 (
        echo   ERROR: Metallisense-Agent setup failed - see output above.
        pause
        exit /b 1
    )
) else (
    echo   Virtual environment found - syncing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt -q
    call deactivate
)

echo   Launching Metallisense-Agent on http://localhost:8001 ...
start "MetalliSense - AI Service (8001)" cmd /k "cd /d "%ROOT%Metallisense-Agent" && call venv\Scripts\activate.bat && python app\main.py"

echo   Waiting for the AI service to come up before starting the backend...
timeout /t 6 /nobreak >nul

REM ============================================================
REM 2) MetalliSense-Node-BE - Express backend
REM ============================================================
echo.
echo [2/3] Preparing MetalliSense-Node-BE...
cd /d "%ROOT%MetalliSense-Node-BE"

if not exist ".env" if exist ".env.example" (
    copy /Y ".env.example" ".env" >nul
    echo   Created .env from .env.example - add your real DB/JWT/Firebase/API-key values.
)

if not exist "node_modules" (
    echo   Installing npm dependencies...
    call npm install
    if errorlevel 1 (
        echo   ERROR: npm install failed for MetalliSense-Node-BE.
        pause
        exit /b 1
    )
) else (
    echo   node_modules already present - skipping install.
)

echo   Launching MetalliSense-Node-BE on http://localhost:3000 ...
start "MetalliSense - Backend (3000)" cmd /k "cd /d "%ROOT%MetalliSense-Node-BE" && npm start"

REM ============================================================
REM 3) Metallisense-frontend - React/Vite UI
REM ============================================================
echo.
echo [3/3] Preparing Metallisense-frontend...
cd /d "%ROOT%Metallisense-frontend"

if not exist ".env" if exist ".env.example" (
    copy /Y ".env.example" ".env" >nul
    echo   Created .env from .env.example.
)

if not exist "node_modules" (
    echo   Installing npm dependencies...
    call npm install
    if errorlevel 1 (
        echo   ERROR: npm install failed for Metallisense-frontend.
        pause
        exit /b 1
    )
) else (
    echo   node_modules already present - skipping install.
)

echo   Launching Metallisense-frontend on http://localhost:5173 ...
start "MetalliSense - Frontend (5173)" cmd /k "cd /d "%ROOT%Metallisense-frontend" && npm run dev"

cd /d "%ROOT%"

echo.
echo ============================================================
echo   All services are launching in separate windows:
echo     AI Service : http://localhost:8001/docs
echo     Backend    : http://localhost:3000/api/v1/health
echo     Frontend   : http://localhost:5173
echo ============================================================
echo.
echo   Fill in each .env with real credentials if this is a first
echo   run - services will start without them but auth/AI/OPC-UA
echo   features will be degraded until they're set.
echo.
echo   Close each service's window (or Ctrl+C inside it) to stop it.
echo ============================================================
pause
