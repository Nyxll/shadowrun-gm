@echo off
setlocal

set PSQL="C:\Program Files\PostgreSQL\17\bin\psql.exe"
set DB_URL=postgresql://postgres:daf562f1a5bccb27ff6a7de5c0b5Wq@db.bxjguoeuqeucfrwabmga.supabase.co:6543/postgres

echo ========================================
echo Uploading Shadowrun GM Data to Supabase
echo ========================================
echo.

echo [1/10] Uploading chunk 1...
%PSQL% %DB_URL% -f supabase-upload-chunk1.sql
if errorlevel 1 (
    echo ERROR: Failed to upload chunk 1
    pause
    exit /b 1
)
echo SUCCESS: Chunk 1 uploaded
echo.

echo [2/10] Uploading chunk 2...
%PSQL% %DB_URL% -f supabase-upload-chunk2.sql
if errorlevel 1 (
    echo ERROR: Failed to upload chunk 2
    pause
    exit /b 1
)
echo SUCCESS: Chunk 2 uploaded
echo.

echo [3/10] Uploading chunk 3...
%PSQL% %DB_URL% -f supabase-upload-chunk3.sql
if errorlevel 1 (
    echo ERROR: Failed to upload chunk 3
    pause
    exit /b 1
)
echo SUCCESS: Chunk 3 uploaded
echo.

echo [4/10] Uploading chunk 4...
%PSQL% %DB_URL% -f supabase-upload-chunk4.sql
if errorlevel 1 (
    echo ERROR: Failed to upload chunk 4
    pause
    exit /b 1
)
echo SUCCESS: Chunk 4 uploaded
echo.

echo [5/10] Uploading chunk 5...
%PSQL% %DB_URL% -f supabase-upload-chunk5.sql
if errorlevel 1 (
    echo ERROR: Failed to upload chunk 5
    pause
    exit /b 1
)
echo SUCCESS: Chunk 5 uploaded
echo.

echo [6/10] Uploading chunk 6...
%PSQL% %DB_URL% -f supabase-upload-chunk6.sql
if errorlevel 1 (
    echo ERROR: Failed to upload chunk 6
    pause
    exit /b 1
)
echo SUCCESS: Chunk 6 uploaded
echo.

echo [7/10] Uploading chunk 7...
%PSQL% %DB_URL% -f supabase-upload-chunk7.sql
if errorlevel 1 (
    echo ERROR: Failed to upload chunk 7
    pause
    exit /b 1
)
echo SUCCESS: Chunk 7 uploaded
echo.

echo [8/10] Uploading chunk 8...
%PSQL% %DB_URL% -f supabase-upload-chunk8.sql
if errorlevel 1 (
    echo ERROR: Failed to upload chunk 8
    pause
    exit /b 1
)
echo SUCCESS: Chunk 8 uploaded
echo.

echo [9/10] Uploading chunk 9...
%PSQL% %DB_URL% -f supabase-upload-chunk9.sql
if errorlevel 1 (
    echo ERROR: Failed to upload chunk 9
    pause
    exit /b 1
)
echo SUCCESS: Chunk 9 uploaded
echo.

echo [10/10] Uploading chunk 10...
%PSQL% %DB_URL% -f supabase-upload-chunk10.sql
if errorlevel 1 (
    echo ERROR: Failed to upload chunk 10
    pause
    exit /b 1
)
echo SUCCESS: Chunk 10 uploaded
echo.

echo ========================================
echo ALL CHUNKS UPLOADED SUCCESSFULLY!
echo ========================================
echo.
echo Your complete Shadowrun GM database has been uploaded to Supabase.
echo.
pause
