@echo off
echo =========================================================================
echo         HOTEL AUTONOMOUS REVENUE AI AGENT - DEMO MODE STARTUP           
echo =========================================================================
echo.

cd /d "%~dp0"

echo [1/4] Checking and installing frontend dependencies...
if not exist "frontend\node_modules\" (
    echo [INFO] First-time setup detected. Running npm install in frontend...
    cd frontend && npm install && cd ..
) else (
    echo [OK] Frontend dependencies already installed.
)

echo.
echo [2/4] Seeding synthetic demo dataset...
python scripts\seed_demo_data.py
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Python demo seeder encountered an issue or python is not in PATH.
)

echo.
echo [3/4] Starting Backend API Server (http://localhost:8000)...
start "Hotel Revenue AI Agent - Backend API" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo [4/4] Starting Frontend Web Application (http://localhost:3000)...
start "Hotel Revenue AI Agent - Frontend Web App" cmd /k "cd frontend && npm run dev"

echo.
echo =========================================================================
echo  Application servers launched in separate windows!
echo  - Frontend Web UI: http://localhost:3000 (or http://localhost:5173)
echo  - Backend API Docs: http://localhost:8000/docs
echo =========================================================================

