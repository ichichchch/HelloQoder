@echo off
echo ========================================
echo   MindMates - Frontend Development
echo ========================================
echo.

cd frontend

echo Installing dependencies...
call npm install

echo.
echo Starting development server on http://localhost:5173
call npm run dev
