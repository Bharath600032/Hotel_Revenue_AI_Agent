Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "         HOTEL AUTONOMOUS REVENUE AI AGENT - STARTUP SCRIPT              " -ForegroundColor Cyan
Write-Host "=========================================================================" -ForegroundColor Cyan

Set-Location -Path $PSScriptRoot

if (-not (Test-Path -Path "frontend\node_modules")) {
    Write-Host "`n[1/4] Installing frontend npm dependencies..." -ForegroundColor Yellow
    Set-Location -Path "frontend"
    npm install
    Set-Location -Path $PSScriptRoot
} else {
    Write-Host "`n[1/4] Frontend dependencies already installed." -ForegroundColor Green
}

Write-Host "`n[2/4] Seeding synthetic demo dataset..." -ForegroundColor Yellow
python scripts\seed_demo_data.py

Write-Host "`n[3/4] Launching Backend API Server on http://localhost:8000 ..." -ForegroundColor Green
Start-Process cmd -ArgumentList "/k cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Write-Host "`n[4/4] Launching Frontend Web App on http://localhost:3000 ..." -ForegroundColor Green
Start-Process cmd -ArgumentList "/k cd frontend && npm run dev"

Write-Host "`n=========================================================================" -ForegroundColor Cyan
Write-Host " Application initialized successfully!" -ForegroundColor Green
Write-Host " - Frontend Web UI: http://localhost:3000 (or http://localhost:5173)" -ForegroundColor Yellow
Write-Host " - API & OpenAPI Docs: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "=========================================================================" -ForegroundColor Cyan

