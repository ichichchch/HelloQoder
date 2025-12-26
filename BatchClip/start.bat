@echo off
echo ========================================
echo BatchClip - Video Processing Pipeline
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if FFmpeg is available
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg is not installed or not in PATH
    echo Please install FFmpeg for video processing to work
    echo.
)

REM Start Backend
echo [1/2] Starting Backend Server...
cd backend
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt -q
start "BatchClip Backend" cmd /k "python -m uvicorn main:app --reload --port 8000"
cd ..

REM Wait for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend
echo [2/2] Starting Frontend...
cd frontend
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt -q
start "BatchClip Frontend" cmd /k "streamlit run app.py --server.port 8501"
cd ..

echo.
echo ========================================
echo BatchClip is running!
echo ----------------------------------------
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:8501
echo API Docs:    http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to exit (servers will keep running)...
pause >nul
