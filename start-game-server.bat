@echo off
echo ========================================
echo Shadowrun GM - Live Game Server
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.

REM Install/update requirements
echo Installing requirements...
pip install -r requirements.txt
echo.

REM Check for .env file
if not exist ".env" (
    echo WARNING: .env file not found!
    echo Please create .env with required variables:
    echo   XAI_API_KEY=your_grok_api_key
    echo   POSTGRES_HOST=127.0.0.1
    echo   POSTGRES_PORT=5434
    echo   POSTGRES_USER=postgres
    echo   POSTGRES_PASSWORD=your_password
    echo   POSTGRES_DB=postgres
    echo.
    pause
    exit /b 1
)

REM Start the server
echo Starting game server...
echo Server will be available at: http://localhost:8000
echo.
python game-server.py

pause
