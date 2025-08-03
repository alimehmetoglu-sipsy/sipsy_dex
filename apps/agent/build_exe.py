#!/usr/bin/env python3
"""
DexAgents Build Script - Create Windows executable with PyInstaller
"""

import os
import sys
import shutil
import subprocess
import platform
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

class ExecutableBuilder:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.build_dir = self.script_dir / "build"
        self.dist_dir = self.script_dir / "dist"
        self.spec_file = self.script_dir / "dexagents_agent.spec"
        
        # Build configuration
        self.build_config = {
            'app_name': 'DexAgentsAgent',
            'version': '2.0.0',
            'description': 'DexAgents Windows Agent',
            'author': 'DexAgents Team',
            'main_script': 'agent_gui.py',
            'icon_file': 'icon.ico',  # Optional
            'console': False,  # GUI application
            'debug': False,
            'onefile': True,
            'upx': False,  # UPX compression
            'strip_binaries': True,
            'exclude_modules': [
                'matplotlib',
                'numpy',
                'scipy',
                'pandas',
                'jupyter',
                'IPython',
                'tornado',
                'pytest',
                'unittest',
            ],
            'hidden_imports': [
                'websockets',
                'psutil',
                'cryptography',
                'tkinter',
                'tkinter.ttk',
                'tkinter.scrolledtext',
                'tkinter.messagebox',
                'tkinter.filedialog',
                'platform',
                'socket',
                'json',
                'logging',
                'threading',
                'asyncio',
                'subprocess',
                'datetime',
                'base64',
                'hashlib',
                'ssl',
                'certifi',
                'requests',
                'urllib3',
            ]
        }
        
        # Windows-specific hidden imports
        if platform.system() == "Windows":
            self.build_config['hidden_imports'].extend([
                'win32api',
                'win32con',
                'win32gui',
                'win32service',
                'wmi',
                'pystray',
                'PIL'
            ])
    
    def check_dependencies(self) -> bool:
        """Check if all required dependencies are installed"""
        print("📦 Checking dependencies...")
        
        required_packages = [
            'pyinstaller',
            'websockets',
            'psutil',
            'requests',
            'cryptography',
            'certifi'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✓ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ✗ {package} (missing)")
        
        if missing_packages:
            print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
            print("Install them with: pip install " + " ".join(missing_packages))
            return False
        
        return True
    
    def create_icon(self):
        """Create application icon if it doesn't exist"""
        icon_path = self.script_dir / self.build_config['icon_file']
        
        if icon_path.exists():
            print(f"Using existing icon: {icon_path}")
            return str(icon_path)
        
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple icon
            size = (256, 256)
            image = Image.new('RGBA', size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(image)
            
            # Draw a simple logo
            margin = size[0] // 8
            draw.rectangle([margin, margin, size[0] - margin, size[1] - margin], 
                          fill=(0, 120, 255, 255), outline=(0, 80, 200, 255), width=4)
            
            # Add text
            text = "DA"
            bbox = draw.textbbox((0, 0), text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = (size[0] - text_width) // 2
            text_y = (size[1] - text_height) // 2
            draw.text((text_x, text_y), text, fill=(255, 255, 255, 255))
            
            # Save as ICO
            image.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            print(f"Created icon: {icon_path}")
            return str(icon_path)
            
        except ImportError:
            print("PIL not available, skipping icon creation")
            return None
        except Exception as e:
            print(f"Error creating icon: {e}")
            return None
    
    def clean_build_dirs(self):
        """Clean build directories"""
        print("🧹 Cleaning build directories...")
        
        for directory in [self.build_dir, self.dist_dir]:
            if directory.exists():
                try:
                    shutil.rmtree(directory)
                    print(f"  Removed: {directory}")
                except Exception as e:
                    print(f"  Warning: Could not remove {directory}: {e}")
    
    def build_executable(self) -> bool:
        """Build the executable using PyInstaller"""
        print(f"🔧 Building {self.build_config['app_name']} executable...")
        
        try:
            main_script = self.script_dir / self.build_config['main_script']
            
            if not main_script.exists():
                raise FileNotFoundError(f"Main script not found: {main_script}")
            
            # Create icon
            icon_path = self.create_icon()
            
            # Build PyInstaller command
            cmd = [
                sys.executable, '-m', 'PyInstaller',
                '--clean',
                '--noconfirm',
                '--onefile' if self.build_config['onefile'] else '--onedir',
                f"--name={self.build_config['app_name']}",
            ]
            
            # Add windowed mode for GUI
            if not self.build_config['console']:
                cmd.append('--windowed')
            
            # Add icon
            if icon_path:
                cmd.append(f'--icon={icon_path}')
            
            # Add data files
            config_file = self.script_dir / 'config.json'
            if config_file.exists():
                if platform.system() == "Windows":
                    cmd.append(f'--add-data={config_file};.')
                else:
                    cmd.append(f'--add-data={config_file}:.')
            
            # Add hidden imports
            for imp in self.build_config['hidden_imports']:
                cmd.append(f'--hidden-import={imp}')
            
            # Add excludes
            for exc in self.build_config['exclude_modules']:
                cmd.append(f'--exclude-module={exc}')
            
            # Add debug options
            if self.build_config['debug']:
                cmd.append('--debug=all')
            
            # Add main script
            cmd.append(str(main_script))
            
            print(f"Running: {' '.join(cmd)}")
            
            # Run PyInstaller
            result = subprocess.run(cmd, cwd=self.script_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Build completed successfully!")
                
                # Find the executable
                exe_name = f"{self.build_config['app_name']}.exe"
                exe_path = self.dist_dir / exe_name
                
                if exe_path.exists():
                    size = exe_path.stat().st_size
                    print(f"Executable created: {exe_path} ({size:,} bytes)")
                    return True
                else:
                    print(f"❌ Executable not found at expected location: {exe_path}")
                    return False
            else:
                print("❌ Build failed!")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False
                
        except Exception as e:
            print(f"Build error: {e}")
            return False
    
    def create_installer_package(self):
        """Create installer package with executable and config"""
        print("📦 Creating installer package...")
        
        exe_name = f"{self.build_config['app_name']}.exe"
        exe_path = self.dist_dir / exe_name
        
        if not exe_path.exists():
            print(f"❌ Executable not found: {exe_path}")
            return False
        
        # Create installer directory
        installer_dir = self.script_dir / "DexAgents_Installer"
        installer_dir.mkdir(exist_ok=True)
        
        # Copy executable
        shutil.copy2(exe_path, installer_dir / exe_name)
        
        # Create default config
        default_config = {
            "server_url": "ws://localhost:8080",
            "api_token": "your-api-token-here",
            "agent_name": "WindowsAgent_{hostname}_{timestamp}",
            "tags": ["windows", "gui-agent"],
            "auto_start": False,
            "minimize_to_tray": True,
            "run_as_service": False,
            "log_level": "INFO",
            "version": self.build_config['version']
        }
        
        with open(installer_dir / "config.json", 'w') as f:
            json.dump(default_config, f, indent=4)
        
        # Create README
        readme_content = f"""# {self.build_config['description']}

Version: {self.build_config['version']}
Built: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Installation

1. Extract all files to a directory
2. Run {exe_name}
3. Configure server settings in the GUI
4. Click "Start Agent" to connect

## Configuration

The agent will create a config.json file on first run. You can modify this file
to configure default settings:

- Server URL: Your DexAgents server WebSocket URL (e.g., ws://localhost:8080)
- API Token: Your server API token
- Agent Name: Custom name for this agent
- Tags: Array of tags for agent classification

## Features

- Modern GUI interface for easy configuration
- Real-time system monitoring
- Automatic connection management with reconnection
- PowerShell command execution
- Log viewing and management
- Encrypted configuration storage
- System tray integration

## Files

- `{exe_name}` - Main agent executable
- `config.json` - Configuration file template
- `logs/` - Log files directory (created automatically)

## System Requirements

- Windows 10 or later
- Network connectivity to DexAgents server
- PowerShell 5.1 or later (usually pre-installed)

## Troubleshooting

- Ensure server is running and accessible
- Check firewall settings for WebSocket connections
- Verify API token is correct
- Check logs for detailed error messages
- Try running as administrator if needed

## Support

For support and documentation, visit: https://docs.dexagents.com

## Version Information

- Application: {self.build_config['description']}
- Version: {self.build_config['version']}
- Build Date: {datetime.now().isoformat()}
- Python Version: {platform.python_version()}
- Platform: {platform.platform()}
"""
        
        with open(installer_dir / "README.txt", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Create batch file for easy running
        batch_content = f"""@echo off
echo Starting DexAgents Windows Agent...
echo.
"{exe_name}"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Agent exited with error code %ERRORLEVEL%
    pause
)
"""
        
        with open(installer_dir / "run_agent.bat", 'w') as f:
            f.write(batch_content)
        
        # Create ZIP file
        import zipfile
        zip_path = self.script_dir / "DexAgents_Installer.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for file_path in installer_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(installer_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Installer package created: {zip_path}")
        print(f"📁 Installer directory: {installer_dir}")
        
        return True
    
    def verify_executable(self) -> bool:
        """Verify the built executable"""
        exe_name = f"{self.build_config['app_name']}.exe"
        exe_path = self.dist_dir / exe_name
        
        if not exe_path.exists():
            print(f"❌ Executable not found: {exe_path}")
            return False
        
        print(f"🔍 Verifying executable: {exe_path}")
        
        # Check file size
        size = exe_path.stat().st_size
        if size < 1024 * 1024:  # Less than 1MB is suspicious
            print(f"⚠️  Warning: Executable is very small ({size} bytes)")
            return False
        
        print(f"File size: {size:,} bytes")
        
        # Try to get version info (Windows only)
        if platform.system() == "Windows":
            try:
                result = subprocess.run([str(exe_path), '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"Version info: {result.stdout.strip()}")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print("Could not get version info (normal for GUI apps)")
            except Exception as e:
                print(f"Version check warning: {e}")
        
        return True
    
    def build(self) -> bool:
        """Main build process"""
        print("="*60)
        print(f"🚀 DexAgents Windows Agent Build Process")
        print("="*60)
        print(f"App: {self.build_config['app_name']} v{self.build_config['version']}")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {platform.python_version()}")
        print()
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Clean previous builds
        self.clean_build_dirs()
        
        # Build executable
        if not self.build_executable():
            return False
        
        # Verify executable
        if not self.verify_executable():
            return False
        
        # Create installer package
        if not self.create_installer_package():
            return False
        
        print()
        print("="*60)
        print("🎉 BUILD COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"Executable: {self.dist_dir / self.build_config['app_name']}.exe")
        print(f"Installer: {self.script_dir / 'DexAgents_Installer.zip'}")
        print(f"Distribution: {self.dist_dir}")
        print()
        
        return True

def main():
    """Main entry point"""
    builder = ExecutableBuilder()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Build DexAgents Windows Agent")
    parser.add_argument('--debug', action='store_true', help='Build debug version')
    parser.add_argument('--console', action='store_true', help='Build console version')
    parser.add_argument('--clean-only', action='store_true', help='Only clean build directories')
    parser.add_argument('--no-upx', action='store_true', help='Disable UPX compression')
    
    args = parser.parse_args()
    
    # Update build config based on arguments
    if args.debug:
        builder.build_config['debug'] = True
        builder.build_config['console'] = True
    
    if args.console:
        builder.build_config['console'] = True
    
    if args.no_upx:
        builder.build_config['upx'] = False
    
    if args.clean_only:
        builder.clean_build_dirs()
        print("Clean completed.")
        return
    
    # Build
    success = builder.build()
    
    if success:
        print("✅ Build process completed successfully!")
        sys.exit(0)
    else:
        print("❌ Build process failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 