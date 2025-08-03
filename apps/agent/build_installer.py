#!/usr/bin/env python3
"""
DexAgents Installer Build Script
Installer EXE'si oluşturma script'i
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_installer():
    """Build installer as executable"""
    print("🔨 Building DexAgents Installer as executable...")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    
    # Install PyInstaller if not installed
    try:
        import PyInstaller
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Build with PyInstaller
    print("🔧 Building installer executable with PyInstaller...")
    
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name=DexAgentsInstaller",    # Executable name
        "--hidden-import=tkinter",     # Include tkinter
        "--hidden-import=requests",    # Include requests
        "--hidden-import=psutil",      # Include psutil
        "--hidden-import=winreg",      # Include winreg for Windows registry
        "--hidden-import=subprocess",  # Include subprocess
        "--hidden-import=shutil",      # Include shutil
        "--hidden-import=zipfile",     # Include zipfile
        "--hidden-import=tempfile",    # Include tempfile
        "installer_gui.py"             # Main installer script
    ]
    
    subprocess.run(pyinstaller_cmd, check=True)
    
    # Copy executable to current directory
    exe_path = Path("dist/DexAgentsInstaller.exe")
    if exe_path.exists():
        shutil.copy(exe_path, "DexAgentsInstaller.exe")
        print(f"✅ Installer executable created: DexAgentsInstaller.exe")
        
        # Create installer package
        create_installer_package()
    else:
        print("❌ Installer executable not found in dist directory")
        
def create_installer_package():
    """Create installer package with executable and documentation"""
    print("📦 Creating installer package...")
    
    # Create installer directory
    installer_dir = Path("DexAgents_Installer")
    installer_dir.mkdir(exist_ok=True)
    
    # Copy installer executable
    if Path("DexAgentsInstaller.exe").exists():
        shutil.copy("DexAgentsInstaller.exe", installer_dir / "DexAgentsInstaller.exe")
    
    # Create default config template
    default_config = {
        "server_url": "http://localhost:8000",
        "api_token": "default_token",
        "agent_name": "agent_installed",
        "tags": ["windows", "installed"],
        "auto_start": True,
        "run_as_service": False,
        "version": "2.1.4"
    }
    
    import json
    with open(installer_dir / "config_template.json", 'w') as f:
        json.dump(default_config, f, indent=4)
    
    # Create README
    readme_content = """# DexAgents Installer

## Installation Guide

### Prerequisites
- Windows 10/11
- Python 3.11+ (will be installed automatically if needed)
- Internet connection for dependency download

### Installation Steps

1. **Run Installer**
   - Double-click `DexAgentsInstaller.exe`
   - The installer will open with a modern GUI

2. **Configure Server Settings**
   - Enter your DexAgents server URL (e.g., http://localhost:8000)
   - Enter your API token
   - Click "Test Connection" to verify settings

3. **Configure Agent Settings**
   - Enter a custom agent name
   - Add tags (comma-separated)
   - Choose installation options

4. **Install**
   - Click "Install DexAgents" when connection test is successful
   - The installer will:
     - Copy files to %USERPROFILE%\\DexAgents
     - Install Python dependencies
     - Create desktop shortcut
     - Configure auto-start (if enabled)

### Features

✅ **Connection Testing**
- Tests server health endpoint
- Validates API token
- Real-time status feedback

✅ **Smart Installation**
- Automatic dependency installation
- Desktop shortcut creation
- Auto-start configuration
- Windows service support

✅ **User-Friendly Interface**
- Modern GUI design
- Progress indicators
- Error handling
- Success notifications

### Installation Directory

The agent will be installed to: `%USERPROFILE%\\DexAgents`

Files installed:
- `agent_gui.py` - Main agent application
- `config.json` - Agent configuration
- `requirements.txt` - Python dependencies
- `start_agent.bat` - Startup script
- `logs/` - Log directory

### Configuration

The installer creates a `config.json` file with your settings:
```json
{
    "server_url": "http://your-server:8000",
    "api_token": "your-token",
    "agent_name": "your-agent-name",
    "tags": ["windows", "installed"],
    "auto_start": true,
    "run_as_service": false
}
```

### Troubleshooting

**Connection Test Fails:**
- Verify server URL is correct
- Check if server is running
- Verify API token is valid
- Check firewall settings

**Installation Fails:**
- Run as administrator
- Check disk space
- Verify Python installation
- Check antivirus software

**Agent Won't Start:**
- Check logs in %USERPROFILE%\\DexAgents\\logs
- Verify configuration file
- Check Python dependencies

### Support

For issues or questions:
1. Check the logs in the installation directory
2. Verify server connectivity
3. Review configuration settings
4. Contact system administrator

### Files

- `DexAgentsInstaller.exe` - Main installer executable
- `config_template.json` - Configuration template
- `README.txt` - This documentation

---
DexAgents Windows Endpoint Management Platform v2.1.4
"""
    
    with open(installer_dir / "README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Create ZIP file
    import zipfile
    zip_path = "DexAgents_Installer.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in installer_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(installer_dir)
                zipf.write(file, arcname)
    
    print(f"✅ Installer package created: {zip_path}")
    print(f"📁 Installer directory: {installer_dir}")
    
    # Cleanup
    if Path("DexAgentsInstaller.exe").exists():
        os.remove("DexAgentsInstaller.exe")
    
    # Clean PyInstaller files
    if Path("dist").exists():
        shutil.rmtree("dist")
    if Path("build").exists():
        shutil.rmtree("build")
    if Path("DexAgentsInstaller.spec").exists():
        os.remove("DexAgentsInstaller.spec")
    
    print("🎉 Installer build completed successfully!")
    print("\n📋 Next Steps:")
    print("1. Test the installer: DexAgents_Installer.exe")
    print("2. Distribute the ZIP file: DexAgents_Installer.zip")
    print("3. Users can run the installer and configure their agents")

if __name__ == "__main__":
    try:
        build_installer()
    except Exception as e:
        print(f"❌ Installer build failed: {e}")
        sys.exit(1) 