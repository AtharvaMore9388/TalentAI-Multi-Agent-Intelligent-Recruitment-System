# TalentAI — Multi-Agent Intelligent Recruitment and Talent Matching System Launcher
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host " TalentAI: Multi-Agent Intelligent Recruitment and Talent Matching System" -ForegroundColor Cyan
Write-Host "===============================================================================" -ForegroundColor Cyan
Write-Host ""

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Backend
Write-Host "[1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

# 2. Start Frontend
Write-Host "[2/2] Starting Next.js Frontend on http://localhost:3001 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev"

Start-Sleep -Seconds 3

Write-Host "Opening http://localhost:3001 in default browser..." -ForegroundColor Green
Start-Process "http://localhost:3001"

Write-Host ""
Write-Host "TalentAI is running!" -ForegroundColor Green
Write-Host "- Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "- Backend API: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "- Swagger Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
