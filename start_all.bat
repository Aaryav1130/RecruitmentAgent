@echo off
title RecruitmentAgent - Launcher
echo ============================================
echo    RecruitmentAgent - Full Stack Launcher
echo ============================================
echo.

set PROJECT_DIR=%~dp0
set VENV_ACTIVATE=%PROJECT_DIR%.venv\Scripts\activate.bat

echo [1/4] Starting Flask Token Server (port 5001)...
start "Flask Token Server" cmd /k "cd /d %PROJECT_DIR%Interview && call %VENV_ACTIVATE% && python livekit_token.py"
timeout /t 2 >nul

echo [2/4] Starting LiveKit Agent...
start "LiveKit Agent" cmd /k "cd /d %PROJECT_DIR%Interview && call %VENV_ACTIVATE% && python agent_runner.py dev"
timeout /t 2 >nul

echo [3/4] Starting React Frontend (port 5173)...
start "React Frontend" cmd /k "cd /d %PROJECT_DIR%Interview\frontend && npm run dev"
timeout /t 3 >nul

echo [4/4] Starting Streamlit App (port 8501)...
start "Streamlit App" cmd /k "cd /d %PROJECT_DIR% && call %VENV_ACTIVATE% && streamlit run main.py"
timeout /t 3 >nul

echo.
echo ============================================
echo    All services started successfully!
echo ============================================
echo.
echo    Streamlit App:    http://localhost:8501
echo    React Frontend:   http://localhost:5173
echo    Flask Server:     http://localhost:5001
echo.
echo    Close this window or press any key to exit.
echo    (The 4 service windows will keep running)
echo ============================================
pause
