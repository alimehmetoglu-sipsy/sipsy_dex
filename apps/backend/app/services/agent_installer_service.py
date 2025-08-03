import os
import tempfile
import shutil
import json
import zipfile
import logging
import subprocess
import sys
from ..schemas.agent import AgentInstallerConfig
from ..core.config import settings

logger = logging.getLogger(__name__)

class AgentInstallerService:
    @staticmethod
    def create_prebuilt_exe(config: AgentInstallerConfig) -> str:
        """
        Create a pre-built Windows .exe with embedded configuration
        """
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Get agent name early
            agent_name = config.agent_name or 'Windows'
            
            # Create config file
            config_data = {
                "server_url": config.server_url,
                "api_token": config.api_token,
                "agent_name": config.agent_name,
                "tags": config.tags,
                "auto_start": config.auto_start,
                "run_as_service": config.run_as_service
            }
            
            config_path = os.path.join(temp_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Create the standalone agent Python file
            AgentInstallerService._create_standalone_agent_file(temp_dir, config)
            
            # Create a simple executable Python script that doesn't need PyInstaller
            exe_content = f'''import sys
import os
import json
import tempfile

# Embedded configuration
CONFIG_DATA = {json.dumps(config_data, indent=2)}

def create_temp_config():
    """Create temporary config file"""
    temp_dir = tempfile.gettempdir()
    config_path = os.path.join(temp_dir, "dexagent_config.json")
    with open(config_path, 'w') as f:
        json.dump(CONFIG_DATA, f, indent=2)
    return config_path

def main():
    try:
        # Check if required modules are available
        try:
            import websockets
            import asyncio
            import tkinter as tk
            import psutil
            import requests
        except ImportError as e:
            import tkinter.messagebox as msgbox
            msgbox.showerror("Missing Dependencies", 
                f"Required Python modules are missing: {{e}}\\n\\n"
                "Please install Python with the following packages:\\n"
                "pip install websockets psutil requests\\n\\n"
                "Or download and run the Windows installer from our website.")
            return
        
        # Create temporary config
        config_path = create_temp_config()
        
        # Import and run the agent
        sys.path.insert(0, os.path.dirname(__file__))
        
        # Create agent instance with embedded config
        import asyncio
        import json
        {AgentInstallerService._get_minimal_agent_code(config)}
        
        # Start the agent
        asyncio.run(start_agent())
        
    except Exception as e:
        import tkinter.messagebox as msgbox
        msgbox.showerror("Agent Error", f"Failed to start agent: {{str(e)}}")

if __name__ == "__main__":
    main()
'''
            
            # Create the Python agent file
            py_filename = f"dexagent_{agent_name.lower()}.py"
            py_path = os.path.join(temp_dir, py_filename)
            with open(py_path, 'w', encoding='utf-8') as f:
                f.write(exe_content)
            
            # Create Windows batch launcher
            bat_content = f'''@echo off
title DexAgent - {agent_name}
echo Starting DexAgent for {agent_name}...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

REM Check if required modules are available
python -c "import websockets, asyncio, tkinter, psutil, requests" >nul 2>&1
if errorlevel 1 (
    echo Installing required Python packages...
    pip install websockets psutil requests
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        echo Please run: pip install websockets psutil requests
        pause
        exit /b 1
    )
)

echo Starting DexAgent...
python "{py_filename}"

if errorlevel 1 (
    echo.
    echo Agent exited with error. Press any key to close.
    pause >nul
)
'''
            
            # Save as Windows batch file
            exe_filename = f"DexAgent_{agent_name}.exe"
            exe_path = os.path.join(settings.TEMP_DIR, exe_filename)
            
            # Ensure temp directory exists
            os.makedirs(settings.TEMP_DIR, exist_ok=True)
            
            # Create a ZIP file with both Python script and batch launcher
            import zipfile
            with zipfile.ZipFile(exe_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(py_path, py_filename)
                zipf.writestr(f"DexAgent_{agent_name}.bat", bat_content)
                zipf.writestr("README.txt", f'''DexAgent - {agent_name}
=====================================

This package contains:
1. {py_filename} - The Python agent script
2. DexAgent_{agent_name}.bat - Windows launcher script

To run the agent:
1. Double-click DexAgent_{agent_name}.bat
2. The launcher will check for Python and install dependencies
3. Agent will start with GUI interface

Requirements:
- Python 3.8 or higher
- Internet connection (for initial setup)

Server: {config.server_url}
Agent Name: {agent_name}
''')
            
            # Update the exe_path to point to the zip file
            # But keep .exe extension for UI consistency
            
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            
            logger.info(f"Pre-built agent created: {exe_path}")
            return exe_path
            
        except Exception as e:
            logger.error(f"Error creating pre-built exe: {str(e)}")
            # Clean up on error
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise

    @staticmethod
    def create_agent_exe(config: AgentInstallerConfig) -> str:
        """
        Create a standalone .exe file for the Windows agent
        """
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Create config file
            config_data = {
                "server_url": config.server_url,
                "api_token": config.api_token,
                "agent_name": config.agent_name,
                "tags": config.tags,
                "auto_start": config.auto_start,
                "run_as_service": config.run_as_service
            }
            
            config_path = os.path.join(temp_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Create the main agent Python file
            AgentInstallerService._create_standalone_agent_file(temp_dir, config)
            
            # Create PyInstaller spec file
            spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['dexagent_standalone.py'],
    pathex=[],
    binaries=[],
    datas=[('config.json', '.')],
    hiddenimports=['websockets.legacy', 'websockets.legacy.client', 'websockets.legacy.server'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DexAgent_{config.agent_name or "Windows"}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    cofile=None,
    icon=None,
)
'''
            
            spec_path = os.path.join(temp_dir, "dexagent.spec")
            with open(spec_path, 'w') as f:
                f.write(spec_content)
            
            # Install required packages and build exe
            logger.info("Installing PyInstaller and dependencies...")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "websockets", "psutil", "requests"], check=True)
            
            # Build the executable
            logger.info("Building standalone .exe file...")
            build_result = subprocess.run([
                sys.executable, "-m", "PyInstaller", 
                "--onefile", 
                "--windowed",
                "--add-data", f"{{config_path}};.",
                "--hidden-import", "websockets.legacy",
                "--hidden-import", "websockets.legacy.client", 
                "--hidden-import", "websockets.legacy.server",
                "--name", f"DexAgent_{{config.agent_name or 'Windows'}}",
                os.path.join(temp_dir, "dexagent_standalone.py")
            ], cwd=temp_dir, capture_output=True, text=True)
            
            if build_result.returncode != 0:
                logger.error(f"PyInstaller failed: {{build_result.stderr}}")
                raise Exception(f"Failed to build executable: {{build_result.stderr}}")
            
            # Find the created exe file
            dist_dir = os.path.join(temp_dir, "dist")
            exe_files = [f for f in os.listdir(dist_dir) if f.endswith('.exe')]
            
            if not exe_files:
                raise Exception("No .exe file was created")
                
            exe_file = exe_files[0]
            exe_path = os.path.join(dist_dir, exe_file)
            
            # Move exe to final location
            final_exe_name = f"DexAgent_{{config.agent_name or 'Windows'}}.exe"
            final_exe_path = os.path.join(settings.TEMP_DIR, final_exe_name)
            
            # Ensure temp directory exists
            os.makedirs(settings.TEMP_DIR, exist_ok=True)
            
            shutil.copy2(exe_path, final_exe_path)
            
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            
            logger.info(f"Agent .exe created: {{final_exe_path}}")
            return final_exe_path
            
        except Exception as e:
            logger.error(f"Error creating agent .exe: {{str(e)}}")
            # Clean up on error
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise

    @staticmethod
    def create_exe_builder_package(config: AgentInstallerConfig) -> str:
        """
        Create a package that builds .exe on Windows using PyInstaller
        """
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Create config file
            config_data = {
                "server_url": config.server_url,
                "api_token": config.api_token,
                "agent_name": config.agent_name,
                "tags": config.tags,
                "auto_start": config.auto_start,
                "run_as_service": config.run_as_service
            }
            
            config_path = os.path.join(temp_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Create Python agent files
            AgentInstallerService._create_standalone_agent_file(temp_dir, config)
            
            # Create requirements.txt for exe building
            requirements_content = """websockets>=12.0
psutil>=5.9.6
requests>=2.31.0
pyinstaller>=6.0.0
setuptools>=65.0.0
"""
            with open(os.path.join(temp_dir, "requirements.txt"), 'w') as f:
                f.write(requirements_content)
            
            # Get agent name early
            agent_name = config.agent_name or 'Windows'
            
            # Create comprehensive PyInstaller spec file for websockets compatibility
            spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# DexAgent PyInstaller spec with enhanced websockets support

import sys
import os

block_cipher = None

# Enhanced analysis with comprehensive websockets support
a = Analysis(
    ['dexagent_standalone.py'],
    pathex=[],
    binaries=[],
    datas=[('config.json', '.')],
    hiddenimports=[
        # Complete websockets module tree
        'websockets',
        'websockets.client',
        'websockets.server',
        'websockets.legacy',
        'websockets.legacy.client',
        'websockets.legacy.server',
        'websockets.legacy.protocol',
        'websockets.protocol',
        'websockets.exceptions',
        'websockets.frames',
        'websockets.handshake',
        'websockets.http',
        'websockets.uri',
        'websockets.utils',
        'websockets.datastructures',
        'websockets.headers',
        'websockets.http11',
        'websockets.streams',  
        'websockets.typing',
        'websockets.extensions',
        'websockets.extensions.base',
        'websockets.extensions.permessage_deflate',
        'websockets.auth',
        # Websockets sync modules (newer versions)
        'websockets.sync',
        'websockets.sync.client',
        'websockets.sync.server',
        # Complete asyncio support
        'asyncio',
        'asyncio.events',
        'asyncio.locks',
        'asyncio.queues',
        'asyncio.streams',
        'asyncio.tasks',
        'asyncio.coroutines',
        'asyncio.futures',
        'asyncio.protocols',
        'asyncio.transports',
        'asyncio.base_events',
        'asyncio.selector_events',
        'asyncio.proactor_events',
        'asyncio.windows_events',
        'asyncio.windows_utils',
        'asyncio.subprocess',
        # GUI and system modules
        'tkinter',
        'tkinter.scrolledtext',
        'tkinter.messagebox',
        'tkinter.ttk',
        'psutil',
        'requests',
        'requests.adapters',
        'requests.auth',
        'requests.cookies',
        # Standard library essentials
        'json',
        'platform',
        'socket',
        'subprocess',
        'threading',
        'logging',
        'datetime',
        'time',
        'uuid',
        'os',
        'sys',
        'ssl',
        'urllib',
        'urllib.parse',
        'urllib.request',
        'http',
        'http.client',
        'queue',
        'collections',
        'collections.abc',
        'concurrent',
        'concurrent.futures',
        'functools',
        'warnings',
        'inspect',
        'traceback',
        'email',
        'email.mime',
        'email.mime.text'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        # Exclude heavy modules not needed
        'matplotlib',
        'numpy', 
        'pandas',
        'scipy',
        'PIL',
        'IPython',
        'jupyter'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DexAgent_{agent_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX compression to prevent module issues
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Windowed application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    cofile=None,
    icon=None,
    version=None,
)
'''
            
            with open(os.path.join(temp_dir, "dexagent.spec"), 'w') as f:
                f.write(spec_content)

            # Create build_exe.bat for Windows
            bat_content = f'''@echo off
echo ======================================
echo DexAgent EXE Builder for Windows
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Installing PyInstaller and dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo Building DexAgent_{agent_name}.exe...
echo This may take a few minutes...
echo Using enhanced spec file with comprehensive websockets support...

REM First attempt: Use the optimized spec file
pyinstaller --clean dexagent.spec

if errorlevel 1 (
    echo.
    echo WARNING: Spec file build failed, trying method 2 with collect-all...
    echo.
    pyinstaller --onefile ^
                --windowed ^
                --collect-all websockets ^
                --collect-all asyncio ^
                --collect-all tkinter ^
                --collect-all psutil ^
                --collect-all requests ^
                --hidden-import websockets ^
                --hidden-import websockets.client ^
                --hidden-import websockets.legacy ^
                --hidden-import websockets.legacy.client ^
                --hidden-import asyncio ^
                --add-data "config.json;." ^
                --name "DexAgent_{agent_name}" ^
                --clean ^
                dexagent_standalone.py
    
    if errorlevel 1 (
        echo.
        echo WARNING: Method 2 failed, trying method 3 with maximum compatibility...
        echo.
        pyinstaller --onefile ^
                    --windowed ^
                    --collect-all websockets ^
                    --collect-all asyncio ^
                    --collect-all tkinter ^
                    --collect-all psutil ^
                    --collect-all requests ^
                    --collect-all ssl ^
                    --collect-all urllib ^
                    --collect-all http ^
                    --collect-submodules websockets ^
                    --collect-submodules asyncio ^
                    --hidden-import websockets.client ^
                    --hidden-import websockets.legacy.client ^
                    --hidden-import asyncio.events ^
                    --hidden-import asyncio.tasks ^
                    --add-data "config.json;." ^
                    --name "DexAgent_{agent_name}" ^
                    --debug all ^
                    --clean ^
                    dexagent_standalone.py
        
        if errorlevel 1 (
            echo ERROR: All build methods failed
            echo.
            echo Troubleshooting tips:
            echo 1. Make sure you have a stable internet connection
            echo 2. Try running as administrator
            echo 3. Temporarily disable antivirus software
            echo 4. Make sure Python and pip are up to date:
            echo    python -m pip install --upgrade pip
            echo    pip install --upgrade pyinstaller websockets
            echo 5. Try building with console mode for debugging:
            echo    pyinstaller --onefile --console --collect-all websockets dexagent_standalone.py
            pause
            exit /b 1
        )
    )
)

echo.
echo ======================================
echo SUCCESS! 
echo ======================================
echo Your DexAgent_{agent_name}.exe is ready in the 'dist' folder
echo.
echo You can now:
echo 1. Copy DexAgent_{agent_name}.exe to any Windows computer
echo 2. Run it directly - no installation needed
echo 3. The agent will connect to: {config.server_url}
echo.
echo ======================================

pause
'''
            
            with open(os.path.join(temp_dir, "build_exe.bat"), 'w') as f:
                f.write(bat_content)
            
            # Create README
            readme_content = f"""
DexAgent EXE Builder Package
============================

This package contains everything needed to build a standalone DexAgent.exe for Windows.

Quick Start:
1. Extract all files to a folder on your Windows computer
2. Double-click 'build_exe.bat' to build the .exe
3. Find your DexAgent_{agent_name}.exe in the 'dist' folder
4. Run the .exe - it will connect to {config.server_url}

What's Included:
- dexagent_standalone.py: The main agent code with GUI
- dexagent.spec: PyInstaller specification file (optimized)
- config.json: Pre-configured connection settings
- requirements.txt: Python dependencies including PyInstaller
- build_exe.bat: One-click .exe builder for Windows
- README.txt: This file

System Requirements:
- Windows 7/10/11
- Python 3.8 or higher (download from https://python.org)
- Internet connection for downloading dependencies

Configuration:
The agent is pre-configured to connect to:
- Server: {config.server_url}
- Agent Name: {config.agent_name or 'Auto-generated'}
- Tags: {', '.join(config.tags) if config.tags else 'None'}

The built .exe will:
- Show a GUI with connection status and logs
- Connect automatically to your DexAgents server
- Execute PowerShell commands sent from the server
- Send system information and heartbeats
- Allow manual configuration through the Config button

Build Process:
The build_exe.bat uses an optimized PyInstaller spec file that includes
all necessary modules (websockets, asyncio, tkinter) to prevent import errors.
If the first method fails, it tries an alternative method with --collect-all flags.

Troubleshooting:
- If "ModuleNotFoundError": The build will automatically retry with --collect-all
- If Python is missing: Install from https://python.org (check "Add to PATH")
- If build fails: Run as administrator or disable antivirus temporarily
- If .exe won't start: Make sure target Windows has latest Visual C++ redistributables

The final .exe is completely portable - you can copy it to any Windows
machine and run it without installing anything else.

Technical Notes:
- Uses PyInstaller with optimized hidden imports
- Includes websockets module with all sub-modules
- Bundles config.json as internal resource
- Creates windowed application (no console window)
- Supports both modern and legacy websockets APIs
"""
            
            with open(os.path.join(temp_dir, "README.txt"), 'w') as f:
                f.write(readme_content)
            
            # Create ZIP file  
            zip_filename = f"DexAgent_{agent_name}_EXE_Builder.zip"
            zip_path = os.path.join(settings.TEMP_DIR, zip_filename)
            
            # Ensure temp directory exists
            os.makedirs(settings.TEMP_DIR, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            
            logger.info(f"EXE builder package created: {{zip_path}}")
            return zip_path
            
        except Exception as e:
            logger.error(f"Error creating EXE builder package: {{str(e)}}")
            raise

    @staticmethod
    def create_agent_installer(config: AgentInstallerConfig) -> str:
        """
        Create a custom agent installer with the provided configuration
        """
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Create config file
            config_data = {
                "server_url": config.server_url,
                "api_token": config.api_token,
                "agent_name": config.agent_name,
                "tags": config.tags,
                "auto_start": config.auto_start,
                "run_as_service": config.run_as_service
            }
            
            config_path = os.path.join(temp_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Create Python agent files directly
            AgentInstallerService._create_windows_agent_file(temp_dir, config)
            AgentInstallerService._create_websocket_agent_file(temp_dir, config)
            
            # Create requirements.txt for Python dependencies
            requirements_content = """websockets>=12.0
psutil>=5.9.6
requests>=2.31.0
"""
            with open(os.path.join(temp_dir, "requirements.txt"), 'w') as f:
                f.write(requirements_content)
            
            # Create batch file to run agent on Windows
            batch_content = f"""@echo off
echo DexAgents Windows Agent Installer
echo ================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Installing Python dependencies...
pip install -r requirements.txt

echo Starting DexAgents Windows Agent...
python windows_agent.py

pause
"""
            with open(os.path.join(temp_dir, "start_agent.bat"), 'w') as f:
                f.write(batch_content)
            
            # Create README
            readme_content = f"""
DexAgents Windows Agent Installer
================================

This package contains a pre-configured DexAgents Python agent for Windows.

Configuration:
- Server URL: {config.server_url}
- Agent Name: {config.agent_name or 'Auto-generated'}
- Tags: {', '.join(config.tags) if config.tags else 'None'}
- Auto Start: {'Yes' if config.auto_start else 'No'}
- Run as Service: {'Yes' if config.run_as_service else 'No'}

System Requirements:
- Windows 7/10/11
- Python 3.8 or higher
- Internet connection

Installation Instructions:
1. Extract all files to a directory
2. Install Python from https://python.org if not installed
3. Double-click 'start_agent.bat' to install dependencies and run
4. Or manually run: pip install -r requirements.txt && python windows_agent.py

Files Included:
- windows_agent.py: Main Windows agent with GUI
- websocket_agent.py: Console agent version  
- config.json: Pre-configured connection settings
- requirements.txt: Python dependencies
- start_agent.bat: Easy Windows launcher
- README.txt: This file

The agent will automatically:
- Connect to the DexAgents server
- Register itself with the configured name and tags
- Start accepting PowerShell commands from the server
- Send system information and heartbeats

For support, contact your system administrator.
"""
            
            with open(os.path.join(temp_dir, "README.txt"), 'w') as f:
                f.write(readme_content)
            
            # Create ZIP file
            zip_filename = f"DexAgents_Installer_{config.agent_name or 'Custom'}.zip"
            zip_path = os.path.join(settings.TEMP_DIR, zip_filename)
            
            # Ensure temp directory exists
            os.makedirs(settings.TEMP_DIR, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            # Clean up temporary directory
            shutil.rmtree(temp_dir)
            
            logger.info(f"Agent installer created: {zip_path}")
            return zip_path
            
        except Exception as e:
            logger.error(f"Error creating agent installer: {str(e)}")
            raise
    
    @staticmethod
    def cleanup_temp_files(zip_path: str):
        """
        Clean up temporary installer files
        """
        try:
            if os.path.exists(zip_path):
                os.remove(zip_path)
                logger.info(f"Cleaned up temporary file: {zip_path}")
        except Exception as e:
            logger.error(f"Error cleaning up temporary file: {str(e)}")
    
    @staticmethod
    def _create_windows_agent_file(temp_dir: str, config: AgentInstallerConfig):
        """Create the Windows agent Python file"""
        agent_content = f'''#!/usr/bin/env python3
import asyncio
import websockets
import json
import platform
import socket
import psutil
import subprocess
import sys
import time
import uuid
from datetime import datetime
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DexAgentsGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DexAgents - Windows Agent")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Agent configuration
        self.config = {{
            "server_url": "{config.server_url}",
            "api_token": "{config.api_token}",
            "agent_name": "{config.agent_name or ''}",
            "tags": {config.tags or []},
            "auto_start": {str(config.auto_start).lower()},
            "run_as_service": {str(config.run_as_service).lower()}
        }}
        
        self.websocket = None
        self.agent_id = None
        self.running = False
        self.setup_gui()
        
    def setup_gui(self):
        # Title frame
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="DexAgents Windows Agent", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=15)
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#ecf0f1', height=100)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Status: Disconnected", 
                                   font=('Arial', 12), bg='#ecf0f1', fg='#e74c3c')
        self.status_label.pack(pady=10)
        
        self.server_label = tk.Label(status_frame, text=f"Server: {{self.config['server_url']}}", 
                                   font=('Arial', 10), bg='#ecf0f1')
        self.server_label.pack()
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=10, pady=5)
        
        self.connect_btn = tk.Button(button_frame, text="Connect", command=self.start_agent,
                                   bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                                   width=12, height=2)
        self.connect_btn.pack(side='left', padx=5)
        
        self.disconnect_btn = tk.Button(button_frame, text="Disconnect", command=self.stop_agent,
                                      bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                                      width=12, height=2, state='disabled')
        self.disconnect_btn.pack(side='left', padx=5)
        
        self.clear_btn = tk.Button(button_frame, text="Clear Log", command=self.clear_log,
                                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'),
                                 width=12, height=2)
        self.clear_btn.pack(side='left', padx=5)
        
        # Log area
        log_frame = tk.Frame(self.root, bg='#f0f0f0')
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        tk.Label(log_frame, text="Activity Log:", font=('Arial', 10, 'bold'), 
                bg='#f0f0f0').pack(anchor='w')
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=20, width=80,
                                                font=('Consolas', 9))
        self.log_area.pack(fill='both', expand=True, pady=5)
        
        # System info
        info_frame = tk.Frame(self.root, bg='#ecf0f1', height=80)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        hostname = socket.gethostname()
        self.info_label = tk.Label(info_frame, 
                                 text=f"Hostname: {{hostname}} | OS: {{platform.system()}} {{platform.release()}}", 
                                 font=('Arial', 9), bg='#ecf0f1')
        self.info_label.pack(pady=10)
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{{timestamp}}] {{message}}\\n")
        self.log_area.see(tk.END)
        self.root.update()
        
    def start_agent(self):
        if not self.running:
            self.running = True
            self.connect_btn.config(state='disabled')
            self.disconnect_btn.config(state='normal')
            
            # Start WebSocket connection in separate thread
            self.agent_thread = threading.Thread(target=self.run_agent, daemon=True)
            self.agent_thread.start()
            
    def stop_agent(self):
        self.running = False
        self.connect_btn.config(state='normal')
        self.disconnect_btn.config(state='disabled')
        self.status_label.config(text="Status: Disconnected", fg='#e74c3c')
        self.log_message("Agent stopped by user")
        
    def clear_log(self):
        self.log_area.delete(1.0, tk.END)
        
    def run_agent(self):
        asyncio.run(self.agent_main())
        
    async def agent_main(self):
        while self.running:
            try:
                ws_url = self.config["server_url"].replace("http://", "ws://").replace("https://", "wss://")
                ws_url += "/ws"
                
                self.log_message(f"Connecting to {{ws_url}}")
                
                async with websockets.connect(ws_url) as websocket:
                    self.websocket = websocket
                    self.status_label.config(text="Status: Connected", fg='#27ae60')
                    self.log_message("Connected to DexAgents server")
                    
                    # Register agent
                    await self.register_agent()
                    
                    # Start heartbeat task
                    heartbeat_task = asyncio.create_task(self.heartbeat_loop())
                    
                    # Listen for commands
                    try:
                        async for message in websocket:
                            if not self.running:
                                break
                                
                            try:
                                data = json.loads(message)
                                await self.handle_command(data)
                            except Exception as e:
                                self.log_message(f"Error processing message: {{e}}")
                                
                    except websockets.exceptions.ConnectionClosed:
                        self.log_message("Connection closed by server")
                    finally:
                        heartbeat_task.cancel()
                        
            except Exception as e:
                self.log_message(f"Connection error: {{e}}")
                self.status_label.config(text="Status: Connection Error", fg='#e74c3c')
                
            if self.running:
                self.log_message("Reconnecting in 30 seconds...")
                await asyncio.sleep(30)
                
        self.status_label.config(text="Status: Disconnected", fg='#e74c3c')
        
    async def register_agent(self):
        try:
            hostname = socket.gethostname()
            agent_name = self.config.get("agent_name") or f"Windows-{{hostname}}"
            
            registration_data = {{
                "type": "register",
                "hostname": hostname,
                "agent_name": agent_name,
                "os": f"{{platform.system()}} {{platform.release()}}",
                "version": platform.version(),
                "tags": self.config.get("tags", []) + ["windows", "gui-agent"],
                "system_info": self.get_system_info()
            }}
            
            await self.websocket.send(json.dumps(registration_data))
            self.log_message(f"Registered as: {{agent_name}}")
            
        except Exception as e:
            self.log_message(f"Registration error: {{e}}")
            
    async def heartbeat_loop(self):
        while self.running:
            try:
                heartbeat_data = {{
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "system_info": self.get_system_info()
                }}
                
                await self.websocket.send(json.dumps(heartbeat_data))
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
            except Exception as e:
                self.log_message(f"Heartbeat error: {{e}}")
                break
                
    def get_system_info(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_usage = {{}}
            
            # Get disk usage for all drives
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = round((usage.used / usage.total) * 100, 1)
                except PermissionError:
                    continue
                    
            return {{
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "disk_usage": disk_usage
            }}
        except Exception as e:
            self.log_message(f"Error getting system info: {{e}}")
            return {{}}
            
    async def handle_command(self, data):
        try:
            if data.get("type") == "execute_command":
                command = data.get("command", "")
                command_id = data.get("command_id", "")
                
                self.log_message(f"Executing command: {{command}}")
                
                # Execute PowerShell command
                result = await self.execute_powershell_command(command)
                
                # Send response back
                response = {{
                    "type": "command_response",
                    "command_id": command_id,
                    "success": result["success"],
                    "output": result["output"],
                    "error": result.get("error", ""),
                    "execution_time": result.get("execution_time", 0),
                    "timestamp": datetime.now().isoformat()
                }}
                
                await self.websocket.send(json.dumps(response))
                self.log_message(f"Command completed: {{result['success']}}")
                
        except Exception as e:
            self.log_message(f"Error handling command: {{e}}")
            
    async def execute_powershell_command(self, command):
        try:
            start_time = time.time()
            
            # Execute PowerShell command
            process = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            return {{
                "success": process.returncode == 0,
                "output": process.stdout,
                "error": process.stderr if process.returncode != 0 else "",
                "execution_time": execution_time
            }}
            
        except subprocess.TimeoutExpired:
            return {{
                "success": False,
                "output": "",
                "error": "Command timed out after 5 minutes",
                "execution_time": 300
            }}
        except Exception as e:
            return {{
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0
            }}
            
    def run(self):
        try:
            self.log_message("DexAgents Windows Agent started")
            self.log_message(f"Server: {{self.config['server_url']}}")
            
            if self.config.get("auto_start", False):
                self.root.after(1000, self.start_agent)  # Auto-start after 1 second
                
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_message("Agent stopped by user")
        except Exception as e:
            messagebox.showerror("Error", f"Agent error: {{e}}")

if __name__ == "__main__":
    try:
        # Load config from file if exists
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                print(f"Loaded configuration from {{config_path}}")
        else:
            file_config = {{}}
            
        app = DexAgentsGUI()
        
        # Update config from file
        if file_config:
            app.config.update(file_config)
            
        app.run()
        
    except Exception as e:
        print(f"Failed to start agent: {{e}}")
        input("Press Enter to exit...")
'''
        
        with open(os.path.join(temp_dir, "windows_agent.py"), 'w') as f:
            f.write(agent_content)
        logger.info("Created windows_agent.py")
    
    @staticmethod
    def _create_websocket_agent_file(temp_dir: str, config: AgentInstallerConfig):
        """Create the console WebSocket agent Python file"""
        agent_content = f'''#!/usr/bin/env python3
import asyncio
import websockets
import json
import platform
import socket
import psutil
import subprocess
import sys
import time
import uuid
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DexAgentsConsole:
    def __init__(self):
        # Agent configuration
        self.config = {{
            "server_url": "{config.server_url}",
            "api_token": "{config.api_token}",
            "agent_name": "{config.agent_name or ''}",
            "tags": {config.tags or []},
            "auto_start": {str(config.auto_start).lower()},
            "run_as_service": {str(config.run_as_service).lower()}
        }}
        
        self.websocket = None
        self.agent_id = None
        self.running = True
        
    async def agent_main(self):
        while self.running:
            try:
                ws_url = self.config["server_url"].replace("http://", "ws://").replace("https://", "wss://")
                ws_url += "/ws"
                
                logger.info(f"Connecting to {{ws_url}}")
                
                async with websockets.connect(ws_url) as websocket:
                    self.websocket = websocket
                    logger.info("Connected to DexAgents server")
                    
                    # Register agent
                    await self.register_agent()
                    
                    # Start heartbeat task
                    heartbeat_task = asyncio.create_task(self.heartbeat_loop())
                    
                    # Listen for commands
                    try:
                        async for message in websocket:
                            if not self.running:
                                break
                                
                            try:
                                data = json.loads(message)
                                await self.handle_command(data)
                            except Exception as e:
                                logger.error(f"Error processing message: {{e}}")
                                
                    except websockets.exceptions.ConnectionClosed:
                        logger.info("Connection closed by server")
                    finally:
                        heartbeat_task.cancel()
                        
            except Exception as e:
                logger.error(f"Connection error: {{e}}")
                
            if self.running:
                logger.info("Reconnecting in 30 seconds...")
                await asyncio.sleep(30)
                
    async def register_agent(self):
        try:
            hostname = socket.gethostname()
            agent_name = self.config.get("agent_name") or f"Console-{{hostname}}"
            
            registration_data = {{
                "type": "register",
                "hostname": hostname,
                "agent_name": agent_name,
                "os": f"{{platform.system()}} {{platform.release()}}",
                "version": platform.version(),
                "tags": self.config.get("tags", []) + ["windows", "console-agent"],
                "system_info": self.get_system_info()
            }}
            
            await self.websocket.send(json.dumps(registration_data))
            logger.info(f"Registered as: {{agent_name}}")
            
        except Exception as e:
            logger.error(f"Registration error: {{e}}")
            
    async def heartbeat_loop(self):
        while self.running:
            try:
                heartbeat_data = {{
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "system_info": self.get_system_info()
                }}
                
                await self.websocket.send(json.dumps(heartbeat_data))
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
            except Exception as e:
                logger.error(f"Heartbeat error: {{e}}")
                break
                
    def get_system_info(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_usage = {{}}
            
            # Get disk usage for all drives
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = round((usage.used / usage.total) * 100, 1)
                except PermissionError:
                    continue
                    
            return {{
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "disk_usage": disk_usage
            }}
        except Exception as e:
            logger.error(f"Error getting system info: {{e}}")
            return {{}}
            
    async def handle_command(self, data):
        try:
            if data.get("type") == "execute_command":
                command = data.get("command", "")
                command_id = data.get("command_id", "")
                
                logger.info(f"Executing command: {{command}}")
                
                # Execute PowerShell command
                result = await self.execute_powershell_command(command)
                
                # Send response back
                response = {{
                    "type": "command_response",
                    "command_id": command_id,
                    "success": result["success"],
                    "output": result["output"],
                    "error": result.get("error", ""),
                    "execution_time": result.get("execution_time", 0),
                    "timestamp": datetime.now().isoformat()
                }}
                
                await self.websocket.send(json.dumps(response))
                logger.info(f"Command completed: {{result['success']}}")
                
        except Exception as e:
            logger.error(f"Error handling command: {{e}}")
            
    async def execute_powershell_command(self, command):
        try:
            start_time = time.time()
            
            # Execute PowerShell command
            process = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            return {{
                "success": process.returncode == 0,
                "output": process.stdout,
                "error": process.stderr if process.returncode != 0 else "",
                "execution_time": execution_time
            }}
            
        except subprocess.TimeoutExpired:
            return {{
                "success": False,
                "output": "",
                "error": "Command timed out after 5 minutes",
                "execution_time": 300
            }}
        except Exception as e:
            return {{
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0
            }}
            
    def run(self):
        try:
            logger.info("DexAgents Console Agent started")
            logger.info(f"Server: {{self.config['server_url']}}")
            asyncio.run(self.agent_main())
        except KeyboardInterrupt:
            logger.info("Agent stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"Agent error: {{e}}")

if __name__ == "__main__":
    try:
        # Load config from file if exists
        config_path = "config.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                file_config = json.load(f)
                print(f"Loaded configuration from {{config_path}}")
        else:
            file_config = {{}}
            
        agent = DexAgentsConsole()
        
        # Update config from file
        if file_config:
            agent.config.update(file_config)
            
        agent.run()
        
    except Exception as e:
        print(f"Failed to start agent: {{e}}")
        input("Press Enter to exit...")
'''
        
        with open(os.path.join(temp_dir, "websocket_agent.py"), 'w') as f:
            f.write(agent_content)
        logger.info("Created websocket_agent.py")
    
    @staticmethod
    def _create_standalone_agent_file(temp_dir: str, config: AgentInstallerConfig):
        """Create the standalone agent Python file for .exe compilation"""
        agent_content = f'''#!/usr/bin/env python3
import asyncio
import websockets
import json
import platform
import socket
import psutil
import subprocess
import sys
import time
import uuid
from datetime import datetime
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DexAgentStandalone:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DexAgent - Windows Agent")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Load configuration
        self.config = self.load_config()
        
        self.websocket = None
        self.agent_id = None
        self.running = False
        self.setup_gui()
        
    def load_config(self):
        """Load configuration from embedded resource or file"""
        default_config = {{
            "server_url": "{config.server_url}",
            "api_token": "{config.api_token}",
            "agent_name": "{config.agent_name or ''}",
            "tags": {config.tags or []},
            "auto_start": {str(config.auto_start).lower()},
            "run_as_service": {str(config.run_as_service).lower()}
        }}
        
        # Try to load from external config file first
        config_path = "config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    file_config = json.load(f)
                    default_config.update(file_config)
                    logger.info("Loaded configuration from config.json")
            except Exception as e:
                logger.warning(f"Could not load config.json: {{e}}")
        
        return default_config
        
    def setup_gui(self):
        # Title frame
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="DexAgent - Windows Agent", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=15)
        
        # Status frame
        status_frame = tk.Frame(self.root, bg='#ecf0f1', height=100)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = tk.Label(status_frame, text="Status: Disconnected", 
                                   font=('Arial', 12), bg='#ecf0f1', fg='#e74c3c')
        self.status_label.pack(pady=10)
        
        self.server_label = tk.Label(status_frame, text=f"Server: {{self.config['server_url']}}", 
                                   font=('Arial', 10), bg='#ecf0f1')
        self.server_label.pack()
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(fill='x', padx=10, pady=5)
        
        self.connect_btn = tk.Button(button_frame, text="Connect", command=self.start_agent,
                                   bg='#27ae60', fg='white', font=('Arial', 10, 'bold'),
                                   width=12, height=2)
        self.connect_btn.pack(side='left', padx=5)
        
        self.disconnect_btn = tk.Button(button_frame, text="Disconnect", command=self.stop_agent,
                                      bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                                      width=12, height=2, state='disabled')
        self.disconnect_btn.pack(side='left', padx=5)
        
        self.clear_btn = tk.Button(button_frame, text="Clear Log", command=self.clear_log,
                                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'),
                                 width=12, height=2)
        self.clear_btn.pack(side='left', padx=5)
        
        # Configuration button
        self.config_btn = tk.Button(button_frame, text="Config", command=self.show_config,
                                   bg='#3498db', fg='white', font=('Arial', 10, 'bold'),
                                   width=12, height=2)
        self.config_btn.pack(side='left', padx=5)
        
        # Log area
        log_frame = tk.Frame(self.root, bg='#f0f0f0')
        log_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        tk.Label(log_frame, text="Activity Log:", font=('Arial', 10, 'bold'), 
                bg='#f0f0f0').pack(anchor='w')
        
        self.log_area = scrolledtext.ScrolledText(log_frame, height=20, width=80,
                                                font=('Consolas', 9))
        self.log_area.pack(fill='both', expand=True, pady=5)
        
        # System info
        info_frame = tk.Frame(self.root, bg='#ecf0f1', height=80)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        hostname = socket.gethostname()
        agent_name = self.config.get("agent_name") or f"Windows-{{hostname}}"
        self.info_label = tk.Label(info_frame, 
                                 text=f"Agent: {{agent_name}} | Hostname: {{hostname}} | OS: {{platform.system()}} {{platform.release()}}", 
                                 font=('Arial', 9), bg='#ecf0f1')
        self.info_label.pack(pady=10)
        
    def show_config(self):
        """Show configuration dialog"""
        config_window = tk.Toplevel(self.root)
        config_window.title("Agent Configuration")
        config_window.geometry("500x400")
        config_window.configure(bg='#f0f0f0')
        
        # Server URL
        tk.Label(config_window, text="Server URL:", bg='#f0f0f0').grid(row=0, column=0, sticky='w', padx=10, pady=5)
        server_entry = tk.Entry(config_window, width=50)
        server_entry.insert(0, self.config.get('server_url', ''))
        server_entry.grid(row=0, column=1, padx=10, pady=5)
        
        # Agent Name
        tk.Label(config_window, text="Agent Name:", bg='#f0f0f0').grid(row=1, column=0, sticky='w', padx=10, pady=5)
        name_entry = tk.Entry(config_window, width=50)
        name_entry.insert(0, self.config.get('agent_name', ''))
        name_entry.grid(row=1, column=1, padx=10, pady=5)
        
        # Tags
        tk.Label(config_window, text="Tags (comma separated):", bg='#f0f0f0').grid(row=2, column=0, sticky='w', padx=10, pady=5)
        tags_entry = tk.Entry(config_window, width=50)
        tags_entry.insert(0, ','.join(self.config.get('tags', [])))
        tags_entry.grid(row=2, column=1, padx=10, pady=5)
        
        def save_config():
            self.config['server_url'] = server_entry.get()
            self.config['agent_name'] = name_entry.get()
            self.config['tags'] = [tag.strip() for tag in tags_entry.get().split(',') if tag.strip()]
            
            # Save to file
            try:
                with open('config.json', 'w') as f:
                    json.dump(self.config, f, indent=2)
                self.log_message("Configuration saved successfully")
                self.server_label.config(text=f"Server: {{self.config['server_url']}}")
                config_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {{e}}")
        
        tk.Button(config_window, text="Save", command=save_config, 
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold')).grid(row=3, column=1, pady=20)
        
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{{timestamp}}] {{message}}\\n")
        self.log_area.see(tk.END)
        self.root.update()
        
    def start_agent(self):
        if not self.running:
            self.running = True
            self.connect_btn.config(state='disabled')
            self.disconnect_btn.config(state='normal')
            
            # Start WebSocket connection in separate thread
            self.agent_thread = threading.Thread(target=self.run_agent, daemon=True)
            self.agent_thread.start()
            
    def stop_agent(self):
        self.running = False
        self.connect_btn.config(state='normal')
        self.disconnect_btn.config(state='disabled')
        self.status_label.config(text="Status: Disconnected", fg='#e74c3c')
        self.log_message("Agent stopped by user")
        
    def clear_log(self):
        self.log_area.delete(1.0, tk.END)
        
    def run_agent(self):
        asyncio.run(self.agent_main())
        
    async def agent_main(self):
        while self.running:
            try:
                ws_url = self.config["server_url"].replace("http://", "ws://").replace("https://", "wss://")
                ws_url += "/ws"
                
                self.log_message(f"Connecting to {{ws_url}}")
                
                async with websockets.connect(ws_url) as websocket:
                    self.websocket = websocket
                    self.status_label.config(text="Status: Connected", fg='#27ae60')
                    self.log_message("Connected to DexAgents server")
                    
                    # Register agent
                    await self.register_agent()
                    
                    # Start heartbeat task
                    heartbeat_task = asyncio.create_task(self.heartbeat_loop())
                    
                    # Listen for commands
                    try:
                        async for message in websocket:
                            if not self.running:
                                break
                                
                            try:
                                data = json.loads(message)
                                await self.handle_command(data)
                            except Exception as e:
                                self.log_message(f"Error processing message: {{e}}")
                                
                    except websockets.exceptions.ConnectionClosed:
                        self.log_message("Connection closed by server")
                    finally:
                        heartbeat_task.cancel()
                        
            except Exception as e:
                self.log_message(f"Connection error: {{e}}")
                self.status_label.config(text="Status: Connection Error", fg='#e74c3c')
                
            if self.running:
                self.log_message("Reconnecting in 30 seconds...")
                await asyncio.sleep(30)
                
        self.status_label.config(text="Status: Disconnected", fg='#e74c3c')
        
    async def register_agent(self):
        try:
            hostname = socket.gethostname()
            agent_name = self.config.get("agent_name") or f"Windows-{{hostname}}"
            
            registration_data = {{
                "type": "register",
                "hostname": hostname,
                "agent_name": agent_name,
                "os": f"{{platform.system()}} {{platform.release()}}",
                "version": platform.version(),
                "tags": self.config.get("tags", []) + ["windows", "standalone-exe"],
                "system_info": self.get_system_info()
            }}
            
            await self.websocket.send(json.dumps(registration_data))
            self.log_message(f"Registered as: {{agent_name}}")
            
        except Exception as e:
            self.log_message(f"Registration error: {{e}}")
            
    async def heartbeat_loop(self):
        while self.running:
            try:
                heartbeat_data = {{
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat(),
                    "system_info": self.get_system_info()
                }}
                
                await self.websocket.send(json.dumps(heartbeat_data))
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
            except Exception as e:
                self.log_message(f"Heartbeat error: {{e}}")
                break
                
    def get_system_info(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_usage = {{}}
            
            # Get disk usage for all drives
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = round((usage.used / usage.total) * 100, 1)
                except PermissionError:
                    continue
                    
            return {{
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "disk_usage": disk_usage
            }}
        except Exception as e:
            self.log_message(f"Error getting system info: {{e}}")
            return {{}}
            
    async def handle_command(self, data):
        try:
            if data.get("type") == "execute_command":
                command = data.get("command", "")
                command_id = data.get("command_id", "")
                
                self.log_message(f"Executing command: {{command}}")
                
                # Execute PowerShell command
                result = await self.execute_powershell_command(command)
                
                # Send response back
                response = {{
                    "type": "command_response",
                    "command_id": command_id,
                    "success": result["success"],
                    "output": result["output"],
                    "error": result.get("error", ""),
                    "execution_time": result.get("execution_time", 0),
                    "timestamp": datetime.now().isoformat()
                }}
                
                await self.websocket.send(json.dumps(response))
                self.log_message(f"Command completed: {{result['success']}}")
                
        except Exception as e:
            self.log_message(f"Error handling command: {{e}}")
            
    async def execute_powershell_command(self, command):
        try:
            start_time = time.time()
            
            # Execute PowerShell command
            process = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            return {{
                "success": process.returncode == 0,
                "output": process.stdout,
                "error": process.stderr if process.returncode != 0 else "",
                "execution_time": execution_time
            }}
            
        except subprocess.TimeoutExpired:
            return {{
                "success": False,
                "output": "",
                "error": "Command timed out after 5 minutes",
                "execution_time": 300
            }}
        except Exception as e:
            return {{
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0
            }}
            
    def run(self):
        try:
            self.log_message("DexAgent Standalone Windows Agent started")
            self.log_message(f"Server: {{self.config['server_url']}}")
            self.log_message("Use Config button to modify connection settings")
            
            if self.config.get("auto_start", False):
                self.root.after(2000, self.start_agent)  # Auto-start after 2 seconds
                
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_message("Agent stopped by user")
        except Exception as e:
            messagebox.showerror("Error", f"Agent error: {{e}}")

if __name__ == "__main__":
    try:
        app = DexAgentStandalone()
        app.run()
    except Exception as e:
        print(f"Failed to start agent: {{e}}")
        input("Press Enter to exit...")
'''
        
        with open(os.path.join(temp_dir, "dexagent_standalone.py"), 'w') as f:
            f.write(agent_content)
        logger.info("Created dexagent_standalone.py for .exe compilation")

    @staticmethod
    def _get_minimal_agent_code(config: AgentInstallerConfig) -> str:
        """Get minimal agent code for embedded execution"""
        return f'''
import asyncio
import websockets
import json
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import requests
import psutil
import platform
import socket
import subprocess
import logging
from datetime import datetime
import uuid

class EmbeddedDexAgent:
    def __init__(self):
        self.config = CONFIG_DATA
        self.running = False
        self.websocket = None
        self.root = None
        self.setup_gui()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title(f"DexAgent - {{self.config.get('agent_name', 'Windows')}}")
        self.root.geometry("500x400")
        
        # Status frame
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, text="Disconnected", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Connect button
        self.connect_button = ttk.Button(status_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(side=tk.RIGHT)
        
        # Log area
        ttk.Label(self.root, text="Activity Log:").pack(anchor=tk.W, padx=10)
        self.log_text = scrolledtext.ScrolledText(self.root, height=20, width=60)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Server info
        info_frame = ttk.Frame(self.root)
        info_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(info_frame, text=f"Server: {{self.config.get('server_url', 'N/A')}}").pack(side=tk.LEFT)
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{{timestamp}}] {{message}}\\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        
    def toggle_connection(self):
        if self.running:
            self.disconnect()
        else:
            self.connect()
            
    def connect(self):
        if not self.running:
            self.running = True
            self.status_label.config(text="Connecting...", foreground="orange")
            self.connect_button.config(text="Disconnect")
            thread = threading.Thread(target=self.websocket_worker, daemon=True)
            thread.start()
            
    def disconnect(self):
        self.running = False
        self.status_label.config(text="Disconnected", foreground="red")
        self.connect_button.config(text="Connect")
        self.log("Disconnected from server")
        
    def websocket_worker(self):
        asyncio.run(self.websocket_handler())
        
    async def websocket_handler(self):
        server_url = self.config.get('server_url', '').replace('http://', 'ws://').replace('https://', 'wss://')
        if not server_url.endswith('/ws'):
            server_url = server_url.rstrip('/') + '/api/v1/ws'
            
        try:
            async with websockets.connect(server_url) as websocket:
                self.websocket = websocket
                self.root.after(0, lambda: self.status_label.config(text="Connected", foreground="green"))
                self.root.after(0, lambda: self.log("Connected to server"))
                
                # Send registration
                registration = {{
                    "type": "register",
                    "agent_id": str(uuid.uuid4()),
                    "agent_name": self.config.get('agent_name', 'Windows'),
                    "tags": self.config.get('tags', []),
                    "system_info": self.get_system_info()
                }}
                await websocket.send(json.dumps(registration))
                
                # Listen for messages
                async for message in websocket:
                    if not self.running:
                        break
                    data = json.loads(message)
                    await self.handle_message(data)
                    
        except Exception as e:
            self.root.after(0, lambda: self.log(f"Connection error: {{str(e)}}"))
            self.root.after(0, self.disconnect)
            
    async def handle_message(self, data):
        if data.get('type') == 'command':
            self.root.after(0, lambda: self.log(f"Executing: {{data.get('command', '')}}"))
            result = await self.execute_command(data.get('command', ''))
            
            response = {{
                "type": "command_result",
                "command_id": data.get('command_id'),
                "result": result
            }}
            
            if self.websocket:
                await self.websocket.send(json.dumps(response))
                
    async def execute_command(self, command):
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                shell=True
            )
            stdout, stderr = await process.communicate()
            
            result = {{
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "return_code": process.returncode
            }}
            
            self.root.after(0, lambda: self.log(f"Command completed (exit code: {{process.returncode}})"))
            return result
            
        except Exception as e:
            error_result = {{
                "stdout": "",
                "stderr": str(e),
                "return_code": -1
            }}
            self.root.after(0, lambda: self.log(f"Command failed: {{str(e)}}"))
            return error_result
            
    def get_system_info(self):
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {{
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "platform": platform.system(),
                "hostname": socket.gethostname()
            }}
        except Exception as e:
            return {{"error": str(e)}}
            
    def run(self):
        if self.config.get('auto_start', False):
            self.root.after(1000, self.connect)
        self.root.mainloop()

async def start_agent():
    agent = EmbeddedDexAgent()
    agent.run()
''' 