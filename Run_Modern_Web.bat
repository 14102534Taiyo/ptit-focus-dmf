@echo off
if exist "D:\ptit-dashboard-next" (
    cd /d "D:\ptit-dashboard-next"
) else (
    cd /d "%~dp0\frontend"
)
echo ===================================================================
echo   PTIT Focus Statistics - Siam Hydrocarbon Intelligence
echo   Next.js Modern Web Portal (Sovereign Executive UI)
echo   Project Location: D:\ptit-dashboard-next
echo ===================================================================
echo.
echo Starting Modern Web Application on http://localhost:3000 ...
echo.
start http://localhost:3000
npm.cmd run dev
pause
