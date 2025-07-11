@echo off
REM Start Microsoft Edge with debugging enabled for MCP AI Portal Agent
REM Uses the default user profile to maintain login data and authentication

echo Starting Microsoft Edge with debugging enabled...
echo Port: 9222
echo Using default user profile to maintain login data
echo.

REM Close any existing Edge processes to avoid conflicts
echo Checking for existing Edge processes...
tasklist /FI "IMAGENAME eq msedge.exe" 2>NUL | find /I /N "msedge.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Warning: Edge is already running. You may need to close it first.
    echo Press Ctrl+C to cancel or any key to continue...
    pause >nul
)

REM Try the most common Edge installation locations
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    echo Found Edge at: C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222
) else if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    echo Found Edge at: C:\Program Files\Microsoft\Edge\Application\msedge.exe
    start "" "C:\Program Files\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222
) else (
    echo ERROR: Microsoft Edge not found in standard locations.
    echo Please check your Edge installation or modify this script with the correct path.
    echo.
    echo Standard locations:
    echo - C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe
    echo - C:\Program Files\Microsoft\Edge\Application\msedge.exe
    echo.
    pause
    exit /b 1
)

echo.
echo Microsoft Edge should now be starting with debugging enabled.
echo This will use your existing profile with all login data preserved.
echo You can now run the MCP AI Portal Agent.
echo.
echo To verify the connection, check that http://localhost:9222 is accessible.
echo.
pause