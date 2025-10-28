@echo off
echo Starting Supabase CLI upload...
echo.

REM Database connection string
set DB_URL=postgresql://postgres.bxjguoeuqeucfrwabmga:h0WNNseI2Xbm6ZRU1BRtQQJZlIqrIq@aws-0-us-east-1.pooler.supabase.com:6543/postgres

echo Uploading 91 SQL files...
echo.

for /L %%i in (1,1,91) do (
    echo [%%i/91] Uploading supabase-data-ordered-part%%i.sql...
    npx supabase@latest db execute --file supabase-data-ordered-part%%i.sql --db-url "%DB_URL%"
    if errorlevel 1 (
        echo ERROR: Failed to upload part %%i
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo Upload complete!
echo ========================================
pause
