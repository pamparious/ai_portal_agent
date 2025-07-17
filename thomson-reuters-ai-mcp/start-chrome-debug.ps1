# PowerShell script to start Google Chrome with debugging enabled for MCP AI Portal Agent
# Uses the default user profile to maintain login data and authentication

Write-Host "Starting Google Chrome with debugging enabled..." -ForegroundColor Green
Write-Host "Port: 9222" -ForegroundColor Yellow
Write-Host "Using default user profile to maintain login data" -ForegroundColor Yellow
Write-Host ""

# Check for existing Chrome processes
$chromeProcesses = Get-Process -Name "chrome" -ErrorAction SilentlyContinue
if ($chromeProcesses) {
    Write-Host "Warning: Chrome is already running. You may need to close it first." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to cancel or any key to continue..." -ForegroundColor Yellow
    Read-Host
}

# Try the most common Chrome installation locations
$chromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
)

$chromeFound = $false
foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        Write-Host "Found Chrome at: $path" -ForegroundColor Green
        
        # Start Chrome with debugging parameters (no custom user-data-dir to preserve login data)
        $arguments = "--remote-debugging-port=9222"
        Start-Process -FilePath $path -ArgumentList $arguments
        
        $chromeFound = $true
        break
    }
}

if (-not $chromeFound) {
    Write-Host "ERROR: Google Chrome not found in standard locations." -ForegroundColor Red
    Write-Host "Please check your Chrome installation or modify this script with the correct path." -ForegroundColor Red
    Write-Host ""
    Write-Host "Standard locations:" -ForegroundColor Yellow
    Write-Host "- C:\Program Files\Google\Chrome\Application\chrome.exe" -ForegroundColor Yellow
    Write-Host "- C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Google Chrome should now be starting with debugging enabled." -ForegroundColor Green
Write-Host "This will use your existing profile with all login data preserved." -ForegroundColor Cyan
Write-Host "You can now run the MCP AI Portal Agent." -ForegroundColor Green
Write-Host ""
Write-Host "To verify the connection, check that http://localhost:9222 is accessible." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"