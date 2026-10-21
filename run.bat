@echo off
title TalentAI - Multi-Agent Intelligent Recruitment and Talent Matching System
echo ===============================================================================
echo  TalentAI: Multi-Agent Intelligent Recruitment and Talent Matching System
echo ===============================================================================
echo.
echo [1/3] Checking environment...

rem Check if python is available
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in PATH. Please install Python 3.10+.
    pause
    exit /b 1
)

rem Check if npm is available
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm was not found in PATH. Please install Node.js 18+.
    pause
    exit /b 1
)

echo [2/3] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "TalentAI Backend (Port 8000)" cmd /k "cd backend && python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

echo [3/3] Starting Next.js Frontend on http://localhost:3001 ...
start "TalentAI Frontend (Port 3001)" cmd /k "cd frontend && npm run dev"

echo.
echo Waiting for servers to initialize...
timeout /t 3 /nobreak >nul

echo Opening browser at http://localhost:3001 ...
start http://localhost:3001

echo.
echo ===============================================================================
echo  TalentAI is running!
echo  - Frontend: http://localhost:3001
echo  - Backend API: http://127.0.0.1:8000
echo  - Interactive Swagger Docs: http://127.0.0.1:8000/docs
echo ===============================================================================
echo.
pause
