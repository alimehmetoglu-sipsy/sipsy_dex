# DexAgents Agent PowerShell Launcher
Write-Host "Starting DexAgents Agent..." -ForegroundColor Green

# Get the directory where this script is located
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$exePath = Join-Path $scriptDir "dist\DexAgentsAgent.exe"

# Check if the executable exists
if (Test-Path $exePath) {
    Write-Host "Found executable at: $exePath" -ForegroundColor Yellow
    Write-Host "Launching DexAgents Agent..." -ForegroundColor Green
    
    # Start the executable
    Start-Process -FilePath $exePath -Wait
} else {
    Write-Host "Error: DexAgentsAgent.exe not found at: $exePath" -ForegroundColor Red
    Write-Host "Please make sure the executable is built and located in the dist folder." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
} 