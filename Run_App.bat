@echo off
cd /d "%~dp0"
echo ========================================================
echo  PTIT Focus Statistics - DMF Petroleum Production System
echo ========================================================
echo.
echo Starting Web Application on http://localhost:8501 ...
echo.

start http://localhost:8501
python -m streamlit run app.py

pause
