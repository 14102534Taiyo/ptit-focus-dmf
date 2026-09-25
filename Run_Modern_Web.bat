@echo off
cd /d "%~dp0\frontend"
echo ===================================================================
echo   PTIT Focus Statistics - Siam Hydrocarbon Intelligence
echo   Next.js Modern Web Portal (Sovereign Executive UI)
echo   Decoupled GitHub Actions ETL Pipeline ^& Zero-Latency Static Data
echo ===================================================================
echo.
echo Starting Modern Web Application on http://localhost:3000 ...
echo.
start http://localhost:3000
npm.cmd run dev
pause
