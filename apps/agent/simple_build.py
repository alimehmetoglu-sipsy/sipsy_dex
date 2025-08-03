#!/usr/bin/env python3
"""
Simple build script for Modern DexAgents Windows Agent
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🚀 Building Modern DexAgents Windows Agent")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("modern_agent_gui.py").exists():
        print("❌ modern_agent_gui.py not found. Please run from agent directory.")
        return False
    
    # Install dependencies
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "modern_requirements.txt"], check=True)
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
        "--name=DexAgentsModernAgent",
        "--clean",
        "modern_agent_gui.py"
    ]
    
    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print("✅ Executable built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    # Check if executable was created
    exe_path = Path("dist/DexAgentsModernAgent.exe")
    if exe_path.exists():
        print(f"✅ Executable created: {exe_path}")
        
        # Copy to current directory
        shutil.copy(exe_path, "DexAgentsModernAgent.exe")
        print("✅ Executable copied to current directory")
        
        # Create installer directory
        installer_dir = Path("DexAgents_Modern_Installer")
        installer_dir.mkdir(exist_ok=True)
        
        # Copy files
        shutil.copy("DexAgentsModernAgent.exe", installer_dir / "DexAgentsModernAgent.exe")
        
        # Create config
        config = {
            "server_url": "http://localhost:8000",
            "api_token": "",
            "agent_name": "modern_agent",
            "tags": ["windows", "modern-gui"],
            "auto_start": True,
            "run_as_service": False,
            "version": "3.0.0"
        }
        
        import json
        with open(installer_dir / "config.json", 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"✅ Installer package created in: {installer_dir}")
        return True
    else:
        print("❌ Executable not found in dist directory")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Build completed successfully!")
    else:
        print("\n❌ Build failed!")
        sys.exit(1) 