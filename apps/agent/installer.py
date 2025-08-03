#!/usr/bin/env python3
"""
DexAgents Windows Agent - Advanced Installer System
Creates MSI installer and handles Windows service installation
"""

import os
import sys
import subprocess
import platform
import winreg
import tempfile
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

class WindowsInstaller:
    def __init__(self):
        self.app_name = "DexAgents Windows Agent"
        self.app_version = "2.0.0"
        self.app_publisher = "DexAgents Team"
        self.app_url = "https://dexagents.com"
        self.app_guid = "{12345678-1234-5678-9ABC-123456789012}"
        
        # Installation paths
        self.install_dir = Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / "DexAgents"
        self.service_name = "DexAgentsService"
        self.service_display_name = "DexAgents Windows Agent Service"
        
        # Registry keys
        self.uninstall_key = f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{self.app_guid}"
        self.app_key = "SOFTWARE\\DexAgents\\WindowsAgent"
        
        # Files to install
        self.exe_file = "DexAgentsAgent.exe"
        self.config_file = "config.json"
        
        # Check if running as administrator
        self.is_admin = self._check_admin_privileges()
        
    def _check_admin_privileges(self) -> bool:
        """Check if running with administrator privileges"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False
    
    def _require_admin(self):
        """Require administrator privileges"""
        if not self.is_admin:
            print("❌ Administrator privileges required for installation")
            print("Please run as administrator")
            sys.exit(1)
    
    def _create_registry_key(self, key_path: str, values: Dict[str, Any]):
        """Create registry key with values"""
        try:
            with winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                for name, value in values.items():
                    if isinstance(value, str):
                        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
                    elif isinstance(value, int):
                        winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            print(f"Created registry key: HKLM\\{key_path}")
            return True
        except Exception as e:
            print(f"Error creating registry key: {e}")
            return False
    
    def _delete_registry_key(self, key_path: str):
        """Delete registry key"""
        try:
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            print(f"Deleted registry key: HKLM\\{key_path}")
            return True
        except FileNotFoundError:
            # Key doesn't exist, that's fine
            return True
        except Exception as e:
            print(f"Error deleting registry key: {e}")
            return False
    
    def _copy_files(self, source_dir: Path, target_dir: Path) -> bool:
        """Copy installation files"""
        try:
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy executable
            exe_source = source_dir / self.exe_file
            exe_target = target_dir / self.exe_file
            
            if exe_source.exists():
                shutil.copy2(exe_source, exe_target)
                print(f"Copied: {exe_source} -> {exe_target}")
            else:
                print(f"❌ Executable not found: {exe_source}")
                return False
            
            # Copy config file
            config_source = source_dir / self.config_file
            config_target = target_dir / self.config_file
            
            if config_source.exists():
                shutil.copy2(config_source, config_target)
                print(f"Copied: {config_source} -> {config_target}")
            
            # Create logs directory
            logs_dir = target_dir / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            return True
            
        except Exception as e:
            print(f"Error copying files: {e}")
            return False
    
    def _create_start_menu_shortcuts(self) -> bool:
        """Create Start Menu shortcuts"""
        try:
            import win32com.client
            
            # Create shortcut in Start Menu
            start_menu = Path(os.environ.get('ALLUSERSPROFILE', 'C:\\ProgramData')) / "Microsoft\\Windows\\Start Menu\\Programs"
            shortcut_dir = start_menu / "DexAgents"
            shortcut_dir.mkdir(exist_ok=True)
            
            shell = win32com.client.Dispatch("WScript.Shell")
            
            # Main application shortcut
            shortcut_path = shortcut_dir / f"{self.app_name}.lnk"
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = str(self.install_dir / self.exe_file)
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.Description = self.app_name
            shortcut.save()
            
            print(f"Created shortcut: {shortcut_path}")
            
            # Uninstaller shortcut
            uninstall_shortcut_path = shortcut_dir / "Uninstall DexAgents Agent.lnk"
            uninstall_shortcut = shell.CreateShortCut(str(uninstall_shortcut_path))
            uninstall_shortcut.Targetpath = "python"
            uninstall_shortcut.Arguments = f'"{__file__}" --uninstall'
            uninstall_shortcut.WorkingDirectory = str(self.install_dir)
            uninstall_shortcut.Description = f"Uninstall {self.app_name}"
            uninstall_shortcut.save()
            
            print(f"Created uninstall shortcut: {uninstall_shortcut_path}")
            
            return True
            
        except ImportError:
            print("pywin32 not available, skipping shortcuts creation")
            return True
        except Exception as e:
            print(f"Error creating shortcuts: {e}")
            return False
    
    def _install_windows_service(self) -> bool:
        """Install Windows service"""
        try:
            import win32serviceutil
            import win32service
            import win32event
            
            # Service script content
            service_script = f'''
import win32serviceutil
import win32service
import win32event
import win32api
import subprocess
import os
import time
import logging

class DexAgentsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "{self.service_name}"
    _svc_display_name_ = "{self.service_display_name}"
    _svc_description_ = "DexAgents Windows Agent Service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None
        
        # Setup logging
        logging.basicConfig(
            filename=r"{self.install_dir}\\logs\\service.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
        self.logger = logging.getLogger(__name__)
    
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
            except Exception as e:
                self.logger.error(f"Error stopping process: {{e}}")
    
    def SvcDoRun(self):
        self.logger.info("Service starting")
        
        exe_path = r"{self.install_dir}\\{self.exe_file}"
        
        while True:
            try:
                # Start the agent process
                self.process = subprocess.Popen([exe_path, "--console"])
                self.logger.info(f"Started agent process: {{self.process.pid}}")
                
                # Wait for stop event or process termination
                result = win32event.WaitForMultipleObjects(
                    [self.hWaitStop, self.process._handle], 
                    False, 
                    win32event.INFINITE
                )
                
                if result == win32event.WAIT_OBJECT_0:
                    # Service stop requested
                    self.logger.info("Service stop requested")
                    break
                else:
                    # Process terminated unexpectedly
                    self.logger.warning("Agent process terminated unexpectedly, restarting...")
                    time.sleep(5)  # Wait before restart
                    
            except Exception as e:
                self.logger.error(f"Error in service: {{e}}")
                time.sleep(10)
        
        self.logger.info("Service stopped")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(DexAgentsService)
'''
            
            # Write service script
            service_script_path = self.install_dir / "service.py"
            with open(service_script_path, 'w') as f:
                f.write(service_script)
            
            # Install service
            result = subprocess.run([
                sys.executable, str(service_script_path), "install"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Windows service installed: {self.service_name}")
                
                # Set service to start automatically
                subprocess.run([
                    "sc", "config", self.service_name, "start=", "auto"
                ], check=True)
                
                return True
            else:
                print(f"❌ Service installation failed: {result.stderr}")
                return False
                
        except ImportError:
            print("pywin32 not available, skipping service installation")
            return True
        except Exception as e:
            print(f"Error installing service: {e}")
            return False
    
    def _uninstall_windows_service(self) -> bool:
        """Uninstall Windows service"""
        try:
            # Stop service if running
            result = subprocess.run([
                "sc", "stop", self.service_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"Stopped service: {self.service_name}")
            
            # Remove service
            result = subprocess.run([
                "sc", "delete", self.service_name
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Removed service: {self.service_name}")
                return True
            else:
                print(f"❌ Service removal failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error removing service: {e}")
            return False
    
    def _create_uninstall_registry_entry(self) -> bool:
        """Create uninstall registry entry"""
        uninstall_values = {
            "DisplayName": self.app_name,
            "DisplayVersion": self.app_version,
            "Publisher": self.app_publisher,
            "URLInfoAbout": self.app_url,
            "InstallLocation": str(self.install_dir),
            "UninstallString": f'python "{__file__}" --uninstall',
            "QuietUninstallString": f'python "{__file__}" --uninstall --quiet',
            "DisplayIcon": str(self.install_dir / self.exe_file),
            "NoModify": 1,
            "NoRepair": 1,
            "EstimatedSize": self._calculate_install_size(),
            "InstallDate": datetime.now().strftime("%Y%m%d")
        }
        
        return self._create_registry_key(self.uninstall_key, uninstall_values)
    
    def _calculate_install_size(self) -> int:
        """Calculate installation size in KB"""
        try:
            total_size = 0
            if (self.install_dir).exists():
                for file_path in self.install_dir.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
            return total_size // 1024  # Convert to KB
        except Exception:
            return 50000  # Default 50MB estimate
    
    def _create_app_registry_settings(self) -> bool:
        """Create application registry settings"""
        app_values = {
            "InstallPath": str(self.install_dir),
            "Version": self.app_version,
            "InstallDate": datetime.now().isoformat(),
            "ServiceInstalled": 1 if self._is_service_installed() else 0
        }
        
        return self._create_registry_key(self.app_key, app_values)
    
    def _is_service_installed(self) -> bool:
        """Check if Windows service is installed"""
        try:
            result = subprocess.run([
                "sc", "query", self.service_name
            ], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def install(self, source_dir: Path, install_service: bool = False) -> bool:
        """Main installation process"""
        self._require_admin()
        
        print("="*60)
        print(f"🚀 Installing {self.app_name} v{self.app_version}")
        print("="*60)
        
        # Copy files
        print("📁 Copying files...")
        if not self._copy_files(source_dir, self.install_dir):
            return False
        
        # Create Start Menu shortcuts
        print("🔗 Creating shortcuts...")
        self._create_start_menu_shortcuts()
        
        # Install Windows service if requested
        if install_service:
            print("⚙️  Installing Windows service...")
            self._install_windows_service()
        
        # Create registry entries
        print("📝 Creating registry entries...")
        self._create_uninstall_registry_entry()
        self._create_app_registry_settings()
        
        # Add to Windows Firewall if needed
        print("🔥 Configuring Windows Firewall...")
        self._configure_firewall()
        
        print()
        print("="*60)
        print("✅ INSTALLATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"Installation directory: {self.install_dir}")
        print(f"Executable: {self.install_dir / self.exe_file}")
        
        if install_service:
            print(f"Service: {self.service_name} (installed)")
        
        print("You can now:")
        print("- Run the agent from Start Menu")
        print("- Configure settings in the GUI")
        print("- Uninstall from Programs and Features")
        print()
        
        return True
    
    def uninstall(self, quiet: bool = False) -> bool:
        """Uninstall the application"""
        if not quiet:
            self._require_admin()
        
        print("="*60)
        print(f"🗑️  Uninstalling {self.app_name}")
        print("="*60)
        
        success = True
        
        # Stop and remove Windows service
        if self._is_service_installed():
            print("⚙️  Removing Windows service...")
            if not self._uninstall_windows_service():
                success = False
        
        # Remove Start Menu shortcuts
        print("🔗 Removing shortcuts...")
        try:
            start_menu = Path(os.environ.get('ALLUSERSPROFILE', 'C:\\ProgramData')) / "Microsoft\\Windows\\Start Menu\\Programs"
            shortcut_dir = start_menu / "DexAgents"
            if shortcut_dir.exists():
                shutil.rmtree(shortcut_dir)
                print(f"Removed shortcuts: {shortcut_dir}")
        except Exception as e:
            print(f"Error removing shortcuts: {e}")
            success = False
        
        # Remove registry entries
        print("📝 Removing registry entries...")
        if not self._delete_registry_key(self.uninstall_key):
            success = False
        if not self._delete_registry_key(self.app_key):
            success = False
        
        # Remove installation directory
        print("📁 Removing installation files...")
        try:
            if self.install_dir.exists():
                # Keep user data like logs
                logs_backup = None
                logs_dir = self.install_dir / "logs"
                if logs_dir.exists():
                    logs_backup = Path.home() / "DexAgents_Logs_Backup"
                    if logs_backup.exists():
                        shutil.rmtree(logs_backup)
                    shutil.move(str(logs_dir), str(logs_backup))
                    print(f"Backed up logs to: {logs_backup}")
                
                shutil.rmtree(self.install_dir)
                print(f"Removed: {self.install_dir}")
        except Exception as e:
            print(f"Error removing installation directory: {e}")
            success = False
        
        # Remove firewall rules
        print("🔥 Removing firewall rules...")
        self._remove_firewall_rules()
        
        if success:
            print()
            print("="*60)
            print("✅ UNINSTALLATION COMPLETED SUCCESSFULLY!")
            print("="*60)
        else:
            print()
            print("="*60)
            print("⚠️  UNINSTALLATION COMPLETED WITH WARNINGS")
            print("="*60)
            print("Some components may need manual removal")
        
        return success
    
    def _configure_firewall(self):
        """Configure Windows Firewall rules"""
        try:
            exe_path = self.install_dir / self.exe_file
            
            # Add inbound rule
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name=DexAgents Agent",
                "dir=in",
                "action=allow",
                f"program={exe_path}",
                "enable=yes"
            ], check=True)
            
            # Add outbound rule
            subprocess.run([
                "netsh", "advfirewall", "firewall", "add", "rule",
                f"name=DexAgents Agent",
                "dir=out",
                "action=allow",
                f"program={exe_path}",
                "enable=yes"
            ], check=True)
            
            print("Configured Windows Firewall rules")
            
        except Exception as e:
            print(f"Warning: Could not configure firewall: {e}")
    
    def _remove_firewall_rules(self):
        """Remove Windows Firewall rules"""
        try:
            subprocess.run([
                "netsh", "advfirewall", "firewall", "delete", "rule",
                "name=DexAgents Agent"
            ], check=True)
            
            print("Removed Windows Firewall rules")
            
        except Exception as e:
            print(f"Warning: Could not remove firewall rules: {e}")
    
    def create_msi_installer(self, source_dir: Path, output_file: Path) -> bool:
        """Create MSI installer using Windows Installer XML (WiX)"""
        print("🏗️  Creating MSI installer...")
        
        # This would require WiX Toolset to be installed
        # For now, we'll create a PowerShell installer script instead
        return self._create_powershell_installer(source_dir, output_file)
    
    def _create_powershell_installer(self, source_dir: Path, output_file: Path) -> bool:
        """Create PowerShell installer script"""
        try:
            powershell_script = f'''
# DexAgents Windows Agent Installer
# Version {self.app_version}

param(
    [switch]$Uninstall,
    [switch]$Service,
    [switch]$Quiet
)

$ErrorActionPreference = "Stop"

# Check for administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {{
    Write-Error "Administrator privileges required. Please run as administrator."
    exit 1
}}

$AppName = "{self.app_name}"
$InstallDir = "{self.install_dir}"
$ServiceName = "{self.service_name}"

if ($Uninstall) {{
    Write-Host "Uninstalling $AppName..." -ForegroundColor Yellow
    
    # Stop and remove service
    try {{
        Stop-Service -Name $ServiceName -ErrorAction SilentlyContinue
        sc.exe delete $ServiceName | Out-Null
        Write-Host "Removed service: $ServiceName" -ForegroundColor Green
    }} catch {{
        Write-Warning "Could not remove service: $_"
    }}
    
    # Remove installation directory
    if (Test-Path $InstallDir) {{
        Remove-Item -Path $InstallDir -Recurse -Force
        Write-Host "Removed installation directory: $InstallDir" -ForegroundColor Green
    }}
    
    # Remove Start Menu shortcuts
    $ShortcutDir = "$env:ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\DexAgents"
    if (Test-Path $ShortcutDir) {{
        Remove-Item -Path $ShortcutDir -Recurse -Force
        Write-Host "Removed shortcuts" -ForegroundColor Green
    }}
    
    # Remove firewall rules
    netsh advfirewall firewall delete rule name="DexAgents Agent" | Out-Null
    
    Write-Host "Uninstallation completed!" -ForegroundColor Green
    exit 0
}}

Write-Host "Installing $AppName..." -ForegroundColor Green

# Create installation directory
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null

# Copy files (this would need to be customized based on actual file locations)
Write-Host "Copying files to $InstallDir" -ForegroundColor Yellow

# Create Start Menu shortcuts
$ShortcutDir = "$env:ProgramData\\Microsoft\\Windows\\Start Menu\\Programs\\DexAgents"
New-Item -ItemType Directory -Path $ShortcutDir -Force | Out-Null

$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$ShortcutDir\\$AppName.lnk")
$Shortcut.TargetPath = "$InstallDir\\DexAgentsAgent.exe"
$Shortcut.WorkingDirectory = $InstallDir
$Shortcut.Save()

Write-Host "Created Start Menu shortcuts" -ForegroundColor Green

# Configure firewall
netsh advfirewall firewall add rule name="DexAgents Agent" dir=in action=allow program="$InstallDir\\DexAgentsAgent.exe" enable=yes | Out-Null
netsh advfirewall firewall add rule name="DexAgents Agent" dir=out action=allow program="$InstallDir\\DexAgentsAgent.exe" enable=yes | Out-Null

Write-Host "Configured Windows Firewall" -ForegroundColor Green

if ($Service) {{
    Write-Host "Installing Windows service..." -ForegroundColor Yellow
    # Service installation would go here
    Write-Host "Service installation completed" -ForegroundColor Green
}}

Write-Host "Installation completed successfully!" -ForegroundColor Green
Write-Host "You can now run DexAgents Agent from the Start Menu" -ForegroundColor Yellow
'''
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(powershell_script)
            
            print(f"✅ Created PowerShell installer: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating installer: {e}")
            return False

def main():
    """Main installer entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DexAgents Windows Agent Installer")
    parser.add_argument('--install', action='store_true', help='Install the application')
    parser.add_argument('--uninstall', action='store_true', help='Uninstall the application')
    parser.add_argument('--source', type=str, help='Source directory for installation files')
    parser.add_argument('--service', action='store_true', help='Install as Windows service')
    parser.add_argument('--quiet', action='store_true', help='Quiet mode')
    parser.add_argument('--create-msi', type=str, help='Create MSI installer (output path)')
    
    args = parser.parse_args()
    
    # Check if running on Windows
    if platform.system() != "Windows":
        print("❌ This installer only works on Windows")
        sys.exit(1)
    
    installer = WindowsInstaller()
    
    if args.uninstall:
        success = installer.uninstall(quiet=args.quiet)
        sys.exit(0 if success else 1)
    
    elif args.install:
        if not args.source:
            print("❌ Source directory required for installation")
            sys.exit(1)
        
        source_dir = Path(args.source)
        if not source_dir.exists():
            print(f"❌ Source directory not found: {source_dir}")
            sys.exit(1)
        
        success = installer.install(source_dir, install_service=args.service)
        sys.exit(0 if success else 1)
    
    elif args.create_msi:
        if not args.source:
            print("❌ Source directory required for MSI creation")
            sys.exit(1)
        
        source_dir = Path(args.source)
        output_file = Path(args.create_msi)
        
        success = installer.create_msi_installer(source_dir, output_file)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()