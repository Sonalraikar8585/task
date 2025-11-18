@echo off
echo Starting FastAPI Auth Server Tests...
echo ======================================

REM Kill any existing server on port 8000
echo Cleaning up any existing server...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul

REM Start the server in the background
echo Starting server on http://localhost:8000...
start /B python main.py > server.log 2>&1

REM Wait for server to start
echo Waiting for server to be ready...
timeout /t 5 /nobreak > nul

REM Generate a random username for testing
set TEST_USERNAME=testuser%RANDOM%

REM Run newman tests
echo Running Newman tests...
echo ======================================
newman run --env-var baseUrl="http://localhost:8000" --env-var username="%TEST_USERNAME%" https://raw.githubusercontent.com/UXGorilla/hiring-backend/main/collection.json

set NEWMAN_EXIT_CODE=%ERRORLEVEL%

REM Cleanup
echo.
echo Cleaning up...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /F /PID %%a 2>nul
del server.log 2>nul

if %NEWMAN_EXIT_CODE% equ 0 (
    echo All tests passed!
    exit /b 0
) else (
    echo Some tests failed
    exit /b 1
)