@echo off
chcp 65001 > nul
echo ========================================
echo   MindMates - Start All Services
echo ========================================
echo.
echo [!] 确保 PostgreSQL 数据库已运行
echo     默认配置: localhost:5432, 数据库: mindmates
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
echo 开发流程:
echo   1. 确保 PostgreSQL 运行中
echo   2. 打开 http://localhost:5173 访问前端
echo   3. 点击"开始新对话"开始聊天
echo.
echo Press any key to exit...
pause > nul
