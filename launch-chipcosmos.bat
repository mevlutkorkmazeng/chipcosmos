@echo off
setlocal
set "ROOT=%~dp0"
title ChipCosmos Launcher

echo ============================================
echo   ChipCosmos baslatiliyor...
echo ============================================
echo.

echo [1/3] Backend (FastAPI) baslatiliyor...
start "ChipCosmos - Backend" cmd /k "cd /d "%ROOT%backend" && "%ROOT%venv\Scripts\python.exe" -m uvicorn main:app --port 8000"

timeout /t 4 /nobreak >nul

echo [2/3] Frontend (Vite) baslatiliyor...
start "ChipCosmos - Frontend" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

timeout /t 5 /nobreak >nul

echo [3/3] Tarayici aciliyor...
start "" "http://localhost:5173"

echo.
echo Hazir! Bu pencereyi kapatabilirsiniz - backend ve frontend
echo kendi pencerelerinde calismaya devam edecek.
echo Kapatmak icin o pencereleri kapatin ya da Ctrl+C yapin.
echo.
pause
