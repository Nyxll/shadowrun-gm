@echo off
echo Stopping existing server...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *game-server*" 2>nul
timeout /t 2 /nobreak >nul
echo Starting server...
start "Shadowrun GM Server" python game-server.py
echo Server restarted!
timeout /t 3 /nobreak >nul
