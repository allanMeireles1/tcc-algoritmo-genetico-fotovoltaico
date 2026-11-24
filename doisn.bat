@echo off
title TCC - Backend + Frontend

cd /d "%~dp0"

echo ============================================
echo  Iniciando Backend FastAPI (uvicorn)...
echo ============================================
start "" cmd /c ".venv\Scripts\python.exe -m uvicorn backend.app:app --reload --port 8000"

echo ============================================
echo  Iniciando Frontend React (Vite)...
echo ============================================
start "" cmd /c "npm --prefix frontend run dev"

echo.
echo Backend disponivel:  http://localhost:8000
echo Frontend disponivel: http://localhost:5173
echo.

pause
