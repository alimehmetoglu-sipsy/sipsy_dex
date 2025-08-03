#!/usr/bin/env python3
"""
Simple build script for Modern DexAgents Windows Agent (No psutil)
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🚀 Building Modern DexAgents Windows Agent (Simplified)")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("modern_agent_gui_simple.py").exists():
        print("❌ modern_agent_gui_simple.py not found. Please run from agent directory.")
        return False
    
    # Install basic dependencies
    print("📦 Installing basic dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    # Build with PyInstaller
    print("🔨 Building executable...")
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name=DexAgentsSimpleAgent",
        "--clean",
        "modern_agent_gui_simple.py"
    ]
    
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print("✅ Executable built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    # Check if executable was created
    exe_path = Path("dist/DexAgentsSimpleAgent.exe")
    if exe_path.exists():
        print(f"✅ Executable created: {exe_path}")
        
        # Copy to current directory
        shutil.copy(exe_path, "DexAgentsSimpleAgent.exe")
        print("✅ Executable copied to current directory")
        
        # Create installer directory
        installer_dir = Path("DexAgents_Simple_Installer")
        installer_dir.mkdir(exist_ok=True)
        
        # Copy files
        shutil.copy("DexAgentsSimpleAgent.exe", installer_dir / "DexAgentsSimpleAgent.exe")
        
        # Create config
        config = {
            "server_url": "http://localhost:8000",
            "api_token": "",
            "agent_name": "simple_agent",
            "tags": ["windows", "simple-gui"],
            "auto_start": True,
            "run_as_service": False,
            "version": "3.0.0-simple"
        }
        
        import json
        with open(installer_dir / "config.json", 'w') as f:
            json.dump(config, f, indent=4)
        
        # Create README
        readme_content = """# DexAgents Simple Windows Agent

## Installation
1. Extract all files to a folder
2. Run DexAgentsSimpleAgent.exe as administrator
3. Configure connection settings
4. Click "Start Agent"

## Features
- Modern GUI interface
- System monitoring (CPU, Memory, Disk)
- Connection testing
- Log management
- No external dependencies (except requests)

## Files
- DexAgentsSimpleAgent.exe - Main executable
- config.json - Configuration file
- logs/ - Log directory

## Troubleshooting
- Run as administrator
- Check server URL and API token
- Verify server is running
- Check logs for errors

Version 3.0.0 Simple - No psutil dependency
"""
        
        with open(installer_dir / "README.txt", 'w') as f:
            f.write(readme_content)
        
        print(f"✅ Simple installer package created in: {installer_dir}")
        return True
    else:
        print("❌ Executable not found in dist directory")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Simple build completed successfully!")
        print("📦 Use DexAgentsSimpleAgent.exe for deployment")
    else:
        print("\n❌ Simple build failed!")
        sys.exit(1) 