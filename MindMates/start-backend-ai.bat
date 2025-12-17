@echo off
echo ========================================
echo   MindMates - AI Backend (Python)
echo ========================================
echo.

cd backend-ai

echo Setting up Python environment...
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Starting FastAPI server on http://localhost:8000
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
