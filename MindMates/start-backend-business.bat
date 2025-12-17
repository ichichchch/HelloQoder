@echo off
echo ========================================
echo   MindMates - Business Backend (.NET)
echo ========================================
echo.

cd backend-business\MindMates.Api

echo Restoring packages...
call dotnet restore

echo.
echo Starting .NET API on http://localhost:5000
call dotnet run
