# PowerShell script to start Microsoft Edge with debugging enabled for MCP AI Portal Agent
# Uses the default user profile to maintain login data and authentication

Write-Host "Starting Microsoft Edge with debugging enabled..." -ForegroundColor Green
Write-Host "Port: 9222" -ForegroundColor Yellow
Write-Host "Using default user profile to maintain login data" -ForegroundColor Yellow
Write-Host ""

# Check for existing Edge processes
$edgeProcesses = Get-Process -Name "msedge" -ErrorAction SilentlyContinue
if ($edgeProcesses) {
    Write-Host "Warning: Edge is already running. You may need to close it first." -ForegroundColor Yellow
    Write-Host "Press Ctrl+C to cancel or any key to continue..." -ForegroundColor Yellow
    Read-Host
}

# Try the most common Edge installation locations
$edgePaths = @(
    "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "C:\Program Files\Microsoft\Edge\Application\msedge.exe"
)

$edgeFound = $false
foreach ($path in $edgePaths) {
    if (Test-Path $path) {
        Write-Host "Found Edge at: $path" -ForegroundColor Green
        
        # Start Edge with debugging parameters (no custom user-data-dir to preserve login data)
        $arguments = "--remote-debugging-port=9222"
        Start-Process -FilePath $path -ArgumentList $arguments
        
        $edgeFound = $true
        break
    }
}

if (-not $edgeFound) {
    Write-Host "ERROR: Microsoft Edge not found in standard locations." -ForegroundColor Red
    Write-Host "Please check your Edge installation or modify this script with the correct path." -ForegroundColor Red
    Write-Host ""
    Write-Host "Standard locations:" -ForegroundColor Yellow
    Write-Host "- C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" -ForegroundColor Yellow
    Write-Host "- C:\Program Files\Microsoft\Edge\Application\msedge.exe" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Microsoft Edge should now be starting with debugging enabled." -ForegroundColor Green
Write-Host "This will use your existing profile with all login data preserved." -ForegroundColor Cyan
Write-Host "You can now run the MCP AI Portal Agent." -ForegroundColor Green
Write-Host ""
Write-Host "To verify the connection, check that http://localhost:9222 is accessible." -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit"