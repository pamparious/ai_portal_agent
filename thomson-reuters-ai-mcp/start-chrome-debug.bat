@echo off
REM Start Google Chrome with debugging enabled for MCP AI Portal Agent
REM Uses the default user profile to maintain login data and authentication

echo Starting Google Chrome with debugging enabled...
echo Port: 9222
echo Using default user profile to maintain login data
echo.

REM Close any existing Chrome processes to avoid conflicts
echo Checking for existing Chrome processes...
tasklist /FI "IMAGENAME eq chrome.exe" 2>NUL | find /I /N "chrome.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Warning: Chrome is already running. You may need to close it first.
    echo Press Ctrl+C to cancel or any key to continue...
    pause >nul
)

REM Try the most common Chrome installation locations
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo Found Chrome at: C:\Program Files\Google\Chrome\Application\chrome.exe
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
) else if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    echo Found Chrome at: C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
    start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
) else (
    echo ERROR: Google Chrome not found in standard locations.
    echo Please check your Chrome installation or modify this script with the correct path.
    echo.
    echo Standard locations:
    echo - C:\Program Files\Google\Chrome\Application\chrome.exe
    echo - C:\Program Files (x86)\Google\Chrome\Application\chrome.exe
    echo.
    pause
    exit /b 1
)

echo.
echo Google Chrome should now be starting with debugging enabled.
echo This will use your existing profile with all login data preserved.
echo You can now run the MCP AI Portal Agent.
echo.
echo To verify the connection, check that http://localhost:9222 is accessible.
echo.
pause