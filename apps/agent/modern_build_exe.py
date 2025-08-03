#!/usr/bin/env python3
"""
Modern DexAgents Windows Agent Build Script
Builds the modern agent GUI as a standalone executable
"""

import os
import sys
import subprocess
import shutil
import json
import zipfile
from pathlib import Path
from datetime import datetime

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "requests", "psutil", "pyinstaller", "pywin32"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", 
                *missing_packages
            ], check=True)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def create_modern_config():
    """Create modern configuration file"""
    print("⚙️ Creating modern configuration...")
    
    modern_config = {
        "server_url": "http://localhost:8000",
        "api_token": "",
        "agent_name": f"modern_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "tags": ["windows", "modern-gui", "v3.0"],
        "auto_start": True,
        "run_as_service": False,
        "version": "3.0.0",
        "created_at": datetime.now().isoformat(),
        "update_interval": 30,
        "connection_timeout": 10,
        "log_level": "INFO",
        "max_log_size": 10485760,  # 10MB
        "backup_logs": True
    }
    
    config_path = Path("modern_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(modern_config, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Configuration created: {config_path}")
    return config_path

def build_executable():
    """Build the modern agent executable"""
    print("🔨 Building modern agent executable...")
    
    # PyInstaller command with modern options
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name=DexAgentsModernAgent",  # Executable name
        "--clean",                      # Clean cache
        "--noconfirm",                  # Overwrite without asking
        "--add-data=modern_config.json;.",  # Include config file
        "--hidden-import=tkinter",      # Include tkinter
        "--hidden-import=requests",     # Include requests
        "--hidden-import=psutil",       # Include psutil
        "--hidden-import=urllib3",      # Include urllib3
        "--hidden-import=cryptography", # Include cryptography
        "--hidden-import=json",         # Include json
        "--hidden-import=threading",    # Include threading
        "--hidden-import=queue",        # Include queue
        "--hidden-import=logging",      # Include logging
        "--hidden-import=datetime",     # Include datetime
        "--hidden-import=pathlib",      # Include pathlib
        "--hidden-import=platform",     # Include platform
        "--hidden-import=webbrowser",   # Include webbrowser
        "--hidden-import=subprocess",   # Include subprocess
        "--hidden-import=shutil",       # Include shutil
        "--hidden-import=os",           # Include os
        "--hidden-import=sys",          # Include sys
        "--hidden-import=time",         # Include time
        "--hidden-import=zipfile",      # Include zipfile
        "modern_agent_gui.py"          # Main script
    ]
    
    # Add icon if exists
    icon_path = Path("icon.ico")
    if icon_path.exists():
        pyinstaller_cmd.extend(["--icon=icon.ico"])
    
    # Add version info if exists
    version_file = Path("version_info.txt")
    if version_file.exists():
        pyinstaller_cmd.extend(["--version-file=version_info.txt"])
    
    try:
        print("🔧 Running PyInstaller...")
        subprocess.run(pyinstaller_cmd, check=True)
        print("✅ PyInstaller completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ PyInstaller failed: {e}")
        return False

def create_modern_installer():
    """Create modern installer package"""
    print("📦 Creating modern installer package...")
    
    # Create installer directory
    installer_dir = Path("DexAgents_Modern_Installer")
    if installer_dir.exists():
        shutil.rmtree(installer_dir)
    installer_dir.mkdir()
    
    # Copy executable
    exe_source = Path("dist/DexAgentsModernAgent.exe")
    if exe_source.exists():
        exe_dest = installer_dir / "DexAgentsModernAgent.exe"
        shutil.copy(exe_source, exe_dest)
        print(f"✅ Copied executable: {exe_dest}")
    else:
        print("❌ Executable not found in dist directory")
        return False
    
    # Copy configuration
    config_source = Path("modern_config.json")
    if config_source.exists():
        config_dest = installer_dir / "config.json"
        shutil.copy(config_source, config_dest)
        print(f"✅ Copied configuration: {config_dest}")
    
    # Create modern README
    readme_content = """# DexAgents Modern Windows Agent

## 🚀 Installation

1. Extract all files to a folder (e.g., `C:\\DexAgents\\`)
2. Run `DexAgentsModernAgent.exe` as administrator
3. Configure connection settings in the modern GUI
4. Click "Start Agent" to begin monitoring

## ⚙️ Configuration

### Connection Settings
- **Server URL**: Your DexAgents server URL (e.g., http://localhost:8000)
- **API Token**: Your server API token (required for authentication)
- **Agent Name**: Custom name for this agent instance
- **Tags**: Comma-separated tags for categorization

### Options
- **Auto-start with Windows**: Automatically start agent on system boot
- **Run as Windows Service**: Run as a Windows service (advanced)

## 🔧 Features

### Modern GUI Interface
- Clean, intuitive user interface
- Real-time system monitoring
- Connection status indicators
- Activity logging with timestamps

### System Monitoring
- CPU usage tracking
- Memory usage monitoring
- Disk space monitoring
- Network status checking

### Advanced Features
- Automatic connection management
- Configurable update intervals
- Comprehensive error handling
- Log file management
- Web interface integration

## 📁 Files

- `DexAgentsModernAgent.exe` - Main agent executable
- `config.json` - Configuration file
- `logs/` - Log files directory (created automatically)

## 🔍 Troubleshooting

### Common Issues

1. **Connection Failed**
   - Verify server URL is correct
   - Check if server is running
   - Ensure API token is valid
   - Check firewall settings

2. **Agent Won't Start**
   - Run as administrator
   - Check antivirus software
   - Verify configuration file

3. **High Resource Usage**
   - Adjust update interval in config
   - Check for multiple instances
   - Review log files

### Log Files

Log files are stored in the `logs/` directory:
- `agent.log` - Main application log
- `error.log` - Error-specific log (if enabled)

### Support

For technical support:
1. Check the logs for error messages
2. Verify server connectivity
3. Review configuration settings
4. Contact system administrator

## 📊 System Requirements

- Windows 10/11 (64-bit)
- 4GB RAM minimum
- 100MB free disk space
- Internet connection for server communication

## 🔄 Updates

The agent will automatically check for updates when connected to the server.
Manual updates can be performed by replacing the executable file.

---
Version 3.0.0 | Modern DexAgents Windows Agent
"""
    
    readme_path = installer_dir / "README.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Create batch installer
    batch_content = """@echo off
echo DexAgents Modern Windows Agent Installer
echo ========================================

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running as administrator - OK
) else (
    echo Please run as administrator
    pause
    exit /b 1
)

REM Create program directory
if not exist "C:\\DexAgents" mkdir "C:\\DexAgents"

REM Copy files
echo Copying files...
copy "DexAgentsModernAgent.exe" "C:\\DexAgents\\" >nul
copy "config.json" "C:\\DexAgents\\" >nul

REM Create logs directory
if not exist "C:\\DexAgents\\logs" mkdir "C:\\DexAgents\\logs"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\DexAgents Agent.lnk'); $Shortcut.TargetPath = 'C:\\DexAgents\\DexAgentsModernAgent.exe'; $Shortcut.WorkingDirectory = 'C:\\DexAgents'; $Shortcut.Save()"

echo Installation completed successfully!
echo.
echo You can now run the agent from:
echo - Desktop shortcut
echo - C:\\DexAgents\\DexAgentsModernAgent.exe
echo.
pause
"""
    
    batch_path = installer_dir / "install.bat"
    with open(batch_path, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    # Create ZIP file
    zip_path = "DexAgents_Modern_Installer.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in installer_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(installer_dir)
                zipf.write(file, arcname)
    
    print(f"✅ Modern installer package created: {zip_path}")
    print(f"📁 Installer directory: {installer_dir}")
    
    return True

def cleanup():
    """Clean up build artifacts"""
    print("🧹 Cleaning up build artifacts...")
    
    # Remove dist and build directories
    for dir_name in ["dist", "build"]:
        dir_path = Path(dir_name)
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"✅ Removed {dir_name} directory")
    
    # Remove spec file
    spec_file = Path("DexAgentsModernAgent.spec")
    if spec_file.exists():
        spec_file.unlink()
        print("✅ Removed spec file")
    
    # Remove temporary config
    temp_config = Path("modern_config.json")
    if temp_config.exists():
        temp_config.unlink()
        print("✅ Removed temporary config")

def main():
    """Main build process"""
    print("🚀 Modern DexAgents Windows Agent Build Process")
    print("=" * 50)
    
    try:
        # Check dependencies
        if not check_dependencies():
            print("❌ Dependency check failed")
            return False
        
        # Create modern config
        create_modern_config()
        
        # Build executable
        if not build_executable():
            print("❌ Executable build failed")
            return False
        
        # Create installer
        if not create_modern_installer():
            print("❌ Installer creation failed")
            return False
        
        # Cleanup
        cleanup()
        
        print("\n🎉 Modern build completed successfully!")
        print("📦 Installer package: DexAgents_Modern_Installer.zip")
        print("📁 Installer directory: DexAgents_Modern_Installer/")
        
        return True
        
    except Exception as e:
        print(f"❌ Build failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 