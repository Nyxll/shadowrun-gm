@echo off
echo Starting Supabase Data Upload via psql...
echo ========================================
echo.

set PSQL="C:\Program Files\PostgreSQL\17\bin\psql.exe"
set DB_URL=postgresql://postgres:h0WNNseI2Xbm6ZRU1BRtQQJZlIqrIq@db.bxjguoeuqeucfrwabmga.supabase.co:5432/postgres

echo Uploading 91 SQL files in order...
echo.

for /L %%i in (1,1,91) do (
    echo [%%i/91] Uploading supabase-data-ordered-part%%i.sql...
    %PSQL% %DB_URL% -f supabase-data-ordered-part%%i.sql
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to upload part %%i
        echo Press any key to exit...
        pause >nul
        exit /b 1
    )
)

echo.
echo ========================================
echo SUCCESS! All 91 files uploaded!
echo ========================================
echo.
pause
