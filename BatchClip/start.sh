#!/bin/bash

echo "========================================"
echo "BatchClip - Video Processing Pipeline"
echo "========================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 is not installed or not in PATH"
    exit 1
fi

# Check if FFmpeg is available
if ! command -v ffmpeg &> /dev/null; then
    echo "[WARNING] FFmpeg is not installed or not in PATH"
    echo "Please install FFmpeg for video processing to work"
    echo ""
fi

# Start Backend
echo "[1/2] Starting Backend Server..."
cd backend
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt -q
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start Frontend
echo "[2/2] Starting Frontend..."
cd frontend
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt -q
streamlit run app.py --server.port 8501 &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "BatchClip is running!"
echo "----------------------------------------"
echo "Backend API: http://localhost:8000"
echo "Frontend UI: http://localhost:8501"
echo "API Docs:    http://localhost:8000/docs"
echo "========================================"
echo ""
echo "Press Ctrl+C to stop all servers..."

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
