@echo off
echo Starting DexAgents Agent...
cd /d "%~dp0"
if exist "dist\DexAgentsAgent.exe" (
    start "" "dist\DexAgentsAgent.exe"
) else (
    echo Error: DexAgentsAgent.exe not found in dist folder
    pause
) 