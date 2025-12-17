@echo off
echo ========================================
echo   MindMates - Start All Services
echo ========================================
echo.
echo Starting all services in separate windows...
echo.

start "MindMates - Frontend" cmd /k "cd /d %~dp0 && call start-frontend.bat"
timeout /t 3 /nobreak > nul

start "MindMates - Business Backend" cmd /k "cd /d %~dp0 && call start-backend-business.bat"
timeout /t 3 /nobreak > nul

start "MindMates - AI Backend" cmd /k "cd /d %~dp0 && call start-backend-ai.bat"

echo.
echo All services are starting!
echo.
echo Services:
echo   - Frontend:         http://localhost:5173
echo   - Business Backend: http://localhost:5000
echo   - AI Backend:       http://localhost:8000
echo.
echo Press any key to exit...
pause > nul
