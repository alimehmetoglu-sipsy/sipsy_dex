#!/usr/bin/env python3
"""
DexAgents Installer GUI
Kurulum için özel GUI uygulaması
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import threading
import requests
from datetime import datetime
from pathlib import Path
import subprocess
import shutil
import zipfile
import tempfile

class DexAgentsInstaller:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DexAgents Installer")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Configuration
        self.config = {
            "server_url": "http://localhost:8000",
            "api_token": "default_token",
            "agent_name": f"agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "tags": ["windows", "installed"],
            "auto_start": True,
            "run_as_service": False
        }
        
        # Test status
        self.test_successful = False
        
        # Create GUI
        self.create_widgets()
        
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="DexAgents Installer", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, text="Windows Endpoint Management Agent", 
                                  font=("Arial", 10))
        subtitle_label.pack(pady=(0, 30))
        
        # Server Configuration Frame
        server_frame = ttk.LabelFrame(main_frame, text="Server Configuration", padding="15")
        server_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Server URL
        ttk.Label(server_frame, text="Server URL:").pack(anchor=tk.W)
        self.server_url_var = tk.StringVar(value=self.config["server_url"])
        self.server_url_entry = ttk.Entry(server_frame, textvariable=self.server_url_var, width=50)
        self.server_url_entry.pack(fill=tk.X, pady=(5, 10))
        
        # API Token
        ttk.Label(server_frame, text="API Token:").pack(anchor=tk.W)
        self.api_token_var = tk.StringVar(value=self.config["api_token"])
        self.api_token_entry = ttk.Entry(server_frame, textvariable=self.api_token_var, width=50, show="*")
        self.api_token_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Test Connection Button
        self.test_button = ttk.Button(server_frame, text="Test Connection", 
                                     command=self.test_connection)
        self.test_button.pack(pady=(0, 10))
        
        # Test Status
        self.test_status_var = tk.StringVar(value="")
        self.test_status_label = ttk.Label(server_frame, textvariable=self.test_status_var, 
                                         font=("Arial", 9))
        self.test_status_label.pack()
        
        # Agent Configuration Frame
        agent_frame = ttk.LabelFrame(main_frame, text="Agent Configuration", padding="15")
        agent_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Agent Name
        ttk.Label(agent_frame, text="Agent Name:").pack(anchor=tk.W)
        self.agent_name_var = tk.StringVar(value=self.config["agent_name"])
        self.agent_name_entry = ttk.Entry(agent_frame, textvariable=self.agent_name_var, width=50)
        self.agent_name_entry.pack(fill=tk.X, pady=(5, 10))
        
        # Tags
        ttk.Label(agent_frame, text="Tags (comma separated):").pack(anchor=tk.W)
        self.tags_var = tk.StringVar(value=", ".join(self.config["tags"]))
        self.tags_entry = ttk.Entry(agent_frame, textvariable=self.tags_var, width=50)
        self.tags_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Options Frame
        options_frame = ttk.LabelFrame(main_frame, text="Installation Options", padding="15")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Auto Start
        self.auto_start_var = tk.BooleanVar(value=self.config["auto_start"])
        auto_start_check = ttk.Checkbutton(options_frame, text="Auto-start after installation", 
                                         variable=self.auto_start_var)
        auto_start_check.pack(anchor=tk.W, pady=2)
        
        # Run as Service
        self.run_as_service_var = tk.BooleanVar(value=self.config["run_as_service"])
        service_check = ttk.Checkbutton(options_frame, text="Run as Windows service", 
                                      variable=self.run_as_service_var)
        service_check.pack(anchor=tk.W, pady=2)
        
        # Install Button Frame
        install_frame = ttk.Frame(main_frame)
        install_frame.pack(pady=(10, 5))
        
        # Install Button
        self.install_button = ttk.Button(install_frame, text="Install DexAgents", 
                                       command=self.install_agent, state=tk.DISABLED)
        self.install_button.pack()
        
        # Install button status
        self.install_status_var = tk.StringVar(value="Install button is disabled until connection test passes")
        self.install_status_label = ttk.Label(install_frame, textvariable=self.install_status_var, 
                                            font=("Arial", 8), foreground="gray")
        self.install_status_label.pack()
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready to install")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                    font=("Arial", 9))
        self.status_label.pack()
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(10, 0))
        
        # Debug info
        self.debug_var = tk.StringVar(value="")
        self.debug_label = ttk.Label(main_frame, textvariable=self.debug_var, 
                                   font=("Arial", 8), foreground="gray")
        self.debug_label.pack()
        
    def test_connection(self):
        """Test connection to the server"""
        self.test_button.config(state=tk.DISABLED)
        self.test_status_var.set("Testing connection...")
        self.progress.start()
        
        # Run test in thread
        thread = threading.Thread(target=self._test_connection_thread)
        thread.daemon = True
        thread.start()
        
    def _test_connection_thread(self):
        """Test connection in background thread"""
        try:
            server_url = self.server_url_var.get().strip()
            api_token = self.api_token_var.get().strip()
            
            if not server_url:
                raise ValueError("Server URL is required")
                
            # Test server health
            health_url = f"{server_url}/api/health"
            response = requests.get(health_url, timeout=10)
            
            if response.status_code == 200:
                # Test API with token
                agents_url = f"{server_url}/api/agents"
                headers = {"Authorization": f"Bearer {api_token}"}
                response = requests.get(agents_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.test_successful = True
                    self.root.after(0, self._test_success)
                else:
                    raise Exception(f"API test failed: {response.status_code}")
            else:
                raise Exception(f"Server health check failed: {response.status_code}")
                
        except Exception as e:
            self.test_successful = False
            self.root.after(0, lambda: self._test_failed(str(e)))
            
    def _test_success(self):
        """Handle successful test"""
        self.test_status_var.set("✅ Connection successful!")
        self.test_status_label.config(foreground="green")
        self.install_button.config(state=tk.NORMAL)
        self.test_button.config(state=tk.NORMAL)
        self.progress.stop()
        
        # Update install button status
        self.install_status_var.set("✅ Connection test passed! Install button is now enabled.")
        self.install_status_label.config(foreground="green")
        
        # Debug info
        self.debug_var.set("✅ Test successful! You can now click Install DexAgents.")
        
        # Force update the GUI
        self.root.update()
        self.root.update_idletasks()
        
    def _test_failed(self, error):
        """Handle failed test"""
        self.test_status_var.set(f"❌ Connection failed: {error}")
        self.test_status_label.config(foreground="red")
        self.install_button.config(state=tk.DISABLED)
        self.test_button.config(state=tk.NORMAL)
        self.progress.stop()
        
        # Update install button status
        self.install_status_var.set("❌ Connection test failed! Install button remains disabled.")
        self.install_status_label.config(foreground="red")
        
        # Debug info
        self.debug_var.set(f"❌ Test failed: {error}")
        
    def install_agent(self):
        """Install the agent"""
        if not self.test_successful:
            messagebox.showerror("Error", "Please test connection first")
            return
            
        # Get configuration
        self.config.update({
            "server_url": self.server_url_var.get().strip(),
            "api_token": self.api_token_var.get().strip(),
            "agent_name": self.agent_name_var.get().strip(),
            "tags": [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()],
            "auto_start": self.auto_start_var.get(),
            "run_as_service": self.run_as_service_var.get()
        })
        
        # Start installation
        self.install_button.config(state=tk.DISABLED)
        self.status_var.set("Installing DexAgents...")
        self.progress.start()
        
        # Run installation in thread
        thread = threading.Thread(target=self._install_thread)
        thread.daemon = True
        thread.start()
        
    def _install_thread(self):
        """Install agent in background thread"""
        try:
            # Create installation directory in Program Files
            if self.config["run_as_service"]:
                install_dir = Path("C:/Program Files/DexAgents")
            else:
                install_dir = Path.home() / "DexAgents"
            
            install_dir.mkdir(exist_ok=True, parents=True)
            
            # Copy agent files
            self.root.after(0, lambda: self.status_var.set("Copying files..."))
            self.root.after(0, lambda: self.debug_var.set(f"Installing to: {install_dir}"))
            
            # Copy current script and dependencies
            current_dir = Path(__file__).parent
            agent_files = [
                "agent_gui.py",
                "requirements.txt",
                "config.json"
            ]
            
            for file in agent_files:
                src = current_dir / file
                dst = install_dir / file
                if src.exists():
                    shutil.copy2(src, dst)
            
            # Create config file
            config_file = install_dir / "config.json"
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            # Create service script
            service_script = install_dir / "dexagents_service.py"
            with open(service_script, 'w') as f:
                f.write('''#!/usr/bin/env python3
"""
DexAgents Windows Service
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import time
import json
import requests
import psutil
import logging
from pathlib import Path
from datetime import datetime

class DexAgentsService(win32serviceutil.ServiceFramework):
    _svc_name_ = "DexAgents"
    _svc_display_name_ = "DexAgents Windows Agent"
    _svc_description_ = "DexAgents Windows Endpoint Management Agent Service"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.running = False
        
        # Setup logging
        log_dir = Path("C:/Program Files/DexAgents/logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "service.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load config
        config_file = Path("C:/Program Files/DexAgents/config.json")
        if config_file.exists():
            with open(config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "server_url": "http://localhost:8000",
                "api_token": "default_token",
                "agent_name": "service_agent",
                "tags": ["windows", "service"],
                "version": "2.1.4"
            }
    
    def SvcStop(self):
        """Stop the service"""
        self.logger.info("Stopping DexAgents service...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.running = False
    
    def SvcDoRun(self):
        """Run the service"""
        self.logger.info("Starting DexAgents service...")
        self.running = True
        self.main()
    
    def main(self):
        """Main service loop"""
        self.logger.info("DexAgents service started")
        
        while self.running:
            try:
                # Get system info
                system_info = {
                    "hostname": socket.gethostname(),
                    "os": "Windows",
                    "cpu_usage": psutil.cpu_percent(),
                    "memory_usage": psutil.virtual_memory().percent,
                    "disk_usage": {partition.device: psutil.disk_usage(partition.mountpoint).percent 
                                  for partition in psutil.disk_partitions()}
                }
                
                # Register with server
                self.register_agent(system_info)
                
                # Wait before next update
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Service error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def register_agent(self, system_info):
        """Register agent with server"""
        try:
            url = f"{self.config['server_url']}/api/agents/register"
            headers = {"Authorization": f"Bearer {self.config['api_token']}"}
            
            data = {
                "hostname": system_info["hostname"],
                "os": system_info["os"],
                "version": self.config.get("version", "2.1.4"),
                "status": "online",
                "tags": self.config.get("tags", ["windows", "service"]),
                "system_info": system_info
            }
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            if response.status_code == 200:
                self.logger.info("Agent registered successfully")
            else:
                self.logger.warning(f"Registration failed: {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"Registration error: {e}")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(DexAgentsService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(DexAgentsService)
''')
            
            # Create startup script
            startup_script = install_dir / "start_agent.bat"
            with open(startup_script, 'w') as f:
                f.write(f'@echo off\n')
                f.write(f'cd /d "{install_dir}"\n')
                if self.config["run_as_service"]:
                    f.write(f'python dexagents_service.py install\n')
                    f.write(f'python dexagents_service.py start\n')
                else:
                    f.write(f'python agent_gui.py\n')
            
            # Install Python dependencies
            self.root.after(0, lambda: self.status_var.set("Installing dependencies..."))
            
            requirements_file = install_dir / "requirements.txt"
            if requirements_file.exists():
                # Add pywin32 for Windows service
                if self.config["run_as_service"]:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", "pywin32"
                    ], check=True, capture_output=True)
                
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
                ], check=True, capture_output=True)
            
            # Install and start Windows service
            if self.config["run_as_service"]:
                self.root.after(0, lambda: self.status_var.set("Installing Windows service..."))
                
                try:
                    # Install service
                    subprocess.run([
                        sys.executable, str(service_script), "install"
                    ], cwd=install_dir, check=True, capture_output=True)
                    
                    # Start service
                    subprocess.run([
                        sys.executable, str(service_script), "start"
                    ], cwd=install_dir, check=True, capture_output=True)
                    
                    self.logger.info("Windows service installed and started successfully")
                    
                except Exception as e:
                    self.logger.error(f"Service installation failed: {e}")
                    # Fallback to regular installation
                    self.config["run_as_service"] = False
            
            # Create desktop shortcut (only if not service)
            if not self.config["run_as_service"]:
                self.root.after(0, lambda: self.status_var.set("Creating shortcuts..."))
                
                desktop = Path.home() / "Desktop"
                shortcut = desktop / "DexAgents.lnk"
                
                # Create VBS script for shortcut
                vbs_script = install_dir / "create_shortcut.vbs"
                with open(vbs_script, 'w') as f:
                    f.write(f'Set WshShell = WScript.CreateObject("WScript.Shell")\n')
                    f.write(f'Set shortcut = WshShell.CreateShortcut("{shortcut}")\n')
                    f.write(f'shortcut.TargetPath = "{sys.executable}"\n')
                    f.write(f'shortcut.Arguments = "{install_dir / "agent_gui.py"}"\n')
                    f.write(f'shortcut.WorkingDirectory = "{install_dir}"\n')
                    f.write(f'shortcut.Description = "DexAgents Windows Agent"\n')
                    f.write(f'shortcut.Save\n')
                
                subprocess.run(["cscript", "//nologo", str(vbs_script)], 
                             cwd=install_dir, check=True, capture_output=True)
            
            # Auto-start if enabled (only if not service)
            if self.config["auto_start"] and not self.config["run_as_service"]:
                self.root.after(0, lambda: self.status_var.set("Configuring auto-start..."))
                
                # Add to startup registry
                import winreg
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
                    winreg.SetValueEx(key, "DexAgents", 0, winreg.REG_SZ, 
                                    f'"{sys.executable}" "{install_dir / "agent_gui.py"}"')
                    winreg.CloseKey(key)
                except Exception as e:
                    print(f"Warning: Could not set auto-start: {e}")
            
            # Installation complete
            self.root.after(0, self._installation_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self._installation_failed(str(e)))
            
    def _installation_complete(self):
        """Handle successful installation"""
        self.progress.stop()
        self.status_var.set("✅ Installation completed successfully!")
        
        result = messagebox.askyesno(
            "Installation Complete",
            "DexAgents has been installed successfully!\n\n"
            "Would you like to start the agent now?"
        )
        
        if result:
            # Start the agent
            install_dir = Path.home() / "DexAgents"
            agent_script = install_dir / "agent_gui.py"
            
            if agent_script.exists():
                subprocess.Popen([sys.executable, str(agent_script)], 
                               cwd=install_dir)
        
        self.root.quit()
        
    def _installation_failed(self, error):
        """Handle failed installation"""
        self.progress.stop()
        self.status_var.set(f"❌ Installation failed: {error}")
        self.install_button.config(state=tk.NORMAL)
        
        messagebox.showerror("Installation Failed", f"Error: {error}")
        
    def run(self):
        """Run the installer"""
        self.root.mainloop()

if __name__ == "__main__":
    installer = DexAgentsInstaller()
    installer.run() 