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
echo Starting Web Server on 0.0.0.0:3000...
echo Browser will automatically open in 3 seconds.
echo (If the browser opens too fast and shows "refused to connect", simply press F5 to refresh)
echo.

start "" cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:3000"

npm.cmd run dev -- -H 0.0.0.0
pause
