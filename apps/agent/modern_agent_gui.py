#!/usr/bin/env python3
"""
DexAgents Modern Windows Agent GUI
A modern, robust agent installation and management interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
import sys
import threading
import time
import requests
import psutil
import platform
import subprocess
import logging
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import queue
import urllib.parse

# Import advanced configuration dialog
try:
    from advanced_config_dialog import AdvancedConfigDialog
    ADVANCED_CONFIG_AVAILABLE = True
except ImportError:
    ADVANCED_CONFIG_AVAILABLE = False

# Import system tray manager
try:
    from tray_manager import SystemTrayManager
    TRAY_AVAILABLE = True
except ImportError as e:
    logging.warning(f"System tray not available: {e}")
    TRAY_AVAILABLE = False

# Import service manager
try:
    from service_manager import ServiceManager
    SERVICE_MANAGER_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Service manager not available: {e}")
    SERVICE_MANAGER_AVAILABLE = False

# Import WebSocket client with PyInstaller compatibility
def _setup_pyinstaller_paths():
    """Add PyInstaller bundle directory to Python path"""
    import sys
    import os
    
    # If running from PyInstaller bundle, add bundle directory to path
    if hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS
        if bundle_dir not in sys.path:
            sys.path.insert(0, bundle_dir)
    
    # Also try current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

# Setup paths for PyInstaller
_setup_pyinstaller_paths()

# Import WebSocket client
try:
    from websocket_client import WebSocketClient
    WEBSOCKET_AVAILABLE = True
except ImportError as e:
    logging.warning(f"WebSocket client not available: {e}")
    WEBSOCKET_AVAILABLE = False

# Configure logging
def setup_logging():
    """Setup comprehensive logging"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_dir / "agent.log")
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

class ModernDexAgentGUI:
    """Modern DexAgents Windows Agent GUI with improved functionality"""
    
    def __init__(self):
        self.logger = setup_logging()
        self.logger.info("Starting Modern DexAgents Windows Agent GUI")
        
        # Initialize variables
        self.agent_running = False
        self.agent_id = None
        self.agent_thread = None
        self.status_queue = queue.Queue()
        self.config = self.load_config()
        
        # Initialize system tray
        self.tray_manager = None
        self.minimize_to_tray = self.config.get("minimize_to_tray", True)
        
        # Initialize service manager
        self.service_manager = None
        if SERVICE_MANAGER_AVAILABLE:
            self.service_manager = ServiceManager(self.logger)
            
        # Startup options
        self.start_minimized = False
        
        # Create main window
        self.setup_main_window()
        self.create_widgets()
        self.setup_status_updates()
        
        # Initialize system tray if available
        if TRAY_AVAILABLE:
            self.setup_system_tray()
        
        # Initialize WebSocket client
        self.websocket_client = None
        if WEBSOCKET_AVAILABLE:
            self.setup_websocket_client()
        
        # Test initial connection
        self.test_connection_async()
        
    def setup_main_window(self):
        """Setup the main application window"""
        self.root = tk.Tk()
        self.root.title("DexAgents Modern Windows Agent")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # Configure window icon if available
        try:
            if Path("icon.ico").exists():
                self.root.iconbitmap("icon.ico")
        except Exception as e:
            self.logger.warning(f"Could not load icon: {e}")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Style configuration
        self.setup_styles()
        
        # Configure window close behavior for tray integration
        if TRAY_AVAILABLE and self.minimize_to_tray:
            self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
            
    def setup_system_tray(self):
        """Setup system tray integration"""
        try:
            self.tray_manager = SystemTrayManager(self)
            
            # Set up callbacks
            self.tray_manager.set_callback('sync_now', self.sync_now)
            self.tray_manager.set_callback('show_config', self.show_configuration_dialog)
            self.tray_manager.set_callback('view_logs', self.open_logs)
            self.tray_manager.set_callback('show_about', self.show_about_dialog)
            self.tray_manager.set_callback('show_main_window', self.show_main_window)
            self.tray_manager.set_callback('exit_application', self.exit_application)
            
            # Start tray in background
            self.tray_manager.start_async()
            
            # Initial status update
            self.tray_manager.update_status("disconnected", "Starting...")
            
            self.logger.info("System tray initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize system tray: {e}")
            self.tray_manager = None
    
    def setup_websocket_client(self):
        """Setup WebSocket client for real-time communication"""
        try:
            server_url = self.config.get("server_url", "http://localhost:8080")
            api_token = self.config.get("api_token", "")
            agent_id = self.agent_id or "temp-agent"
            
            # Initialize WebSocket client with correct parameter order
            self.websocket_client = WebSocketClient(
                agent_id=agent_id,
                server_url=server_url,  # Keep HTTP format, client will convert
                api_token=api_token,
                gui_callback=self._websocket_callback
            )
            
            self.logger.info("WebSocket client initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize WebSocket client: {e}")

    def _websocket_callback(self, event_type: str, data: dict = None):
        """Handle WebSocket events"""
        try:
            self.logger.info(f"WebSocket event: {event_type}")
            
            if event_type == "connected":
                self.status_queue.put(("websocket", "WebSocket connected", "success"))
            elif event_type == "disconnected":
                self.status_queue.put(("websocket", "WebSocket disconnected", "warning"))
            elif event_type == "command_received":
                command = data.get("command", "Unknown command") if data else "Unknown command"
                self.status_queue.put(("command", f"Command received: {command[:50]}...", "info"))
            elif event_type == "command_completed":
                result = data.get("result", {}) if data else {}
                success = result.get("success", False)
                status = "success" if success else "error"
                self.status_queue.put(("command", f"Command completed: {'success' if success else 'failed'}", status))
                
        except Exception as e:
            self.logger.error(f"Error in WebSocket callback: {e}")
            self.websocket_client = None
    
    def start_websocket_connection(self):
        """Start WebSocket connection for real-time communication"""
        if not self.websocket_client:
            self.logger.warning("WebSocket client not available")
            return
            
        try:
            # Update WebSocket client with current agent_id
            if self.agent_id:
                self.websocket_client.agent_id = self.agent_id
            
            # Start WebSocket connection in background
            self.websocket_thread = threading.Thread(target=self._run_websocket, daemon=True)
            self.websocket_thread.start()
            
            self.logger.info("WebSocket connection thread started")
            
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket connection: {e}")
    
    def _run_websocket(self):
        """Run WebSocket client (background thread)"""
        try:
            import asyncio
            
            # Create new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Run the WebSocket client
                loop.run_until_complete(self.websocket_client.run())
            finally:
                loop.close()
                
        except Exception as e:
            self.logger.error(f"WebSocket client error: {e}")
            self.status_queue.put(("websocket", f"WebSocket error: {str(e)}", "error"))
            
    def on_window_close(self):
        """Handle window close event - minimize to tray if enabled"""
        if self.minimize_to_tray and self.tray_manager:
            self.root.withdraw()  # Hide the window
            if self.tray_manager:
                self.tray_manager.show_notification(
                    "DexAgents Agent", 
                    "Application minimized to system tray"
                )
            self.logger.info("Window minimized to system tray")
        else:
            self.exit_application()
            
    def show_main_window(self):
        """Show main window from system tray"""
        self.root.deiconify()  # Show window
        self.root.lift()       # Bring to front
        self.root.focus_force() # Force focus
        self.logger.info("Main window restored from system tray")
        
    def exit_application(self):
        """Exit the application completely"""
        self.logger.info("Exiting application")
        
        # Stop agent if running
        if self.agent_running:
            self.agent_running = False
            
        # Stop system tray
        if self.tray_manager:
            self.tray_manager.stop()
            
        # Stop WebSocket connection
        if self.websocket_client:
            try:
                asyncio.run(self.websocket_client.stop())
            except Exception as e:
                self.logger.error(f"Error stopping WebSocket client: {e}")
            
        # Close main window
        try:
            self.root.quit()
            self.root.destroy()
        except:
            pass
            
        sys.exit(0)
        
    def sync_now(self):
        """Manual sync trigger from system tray"""
        self.logger.info("Manual sync triggered")
        
        if not self.agent_running:
            if self.tray_manager:
                self.tray_manager.show_notification(
                    "Sync Failed", 
                    "Agent is not running. Please start the agent first."
                )
            return
            
        # Trigger immediate status update
        threading.Thread(target=self._perform_sync, daemon=True).start()
        
    def _perform_sync(self):
        """Perform synchronization operation"""
        try:
            # Update status with server
            success = self.update_status()
            
            if success:
                if self.tray_manager:
                    self.tray_manager.show_notification(
                        "Sync Complete", 
                        "Agent synchronized successfully with server"
                    )
                    self.tray_manager.update_status("connected")
                self.log_message("Manual sync completed successfully")
            else:
                if self.tray_manager:
                    self.tray_manager.show_notification(
                        "Sync Failed", 
                        "Failed to synchronize with server"
                    )
                    self.tray_manager.update_status("error")
                self.log_message("Manual sync failed")
                
        except Exception as e:
            self.logger.error(f"Sync error: {e}")
            if self.tray_manager:
                self.tray_manager.show_notification(
                    "Sync Error", 
                    f"Sync failed: {str(e)}"
                )
                self.tray_manager.update_status("error")
                
    def show_configuration_dialog(self):
        """Show configuration dialog (placeholder for now)"""
        # For now, just show the main window - will be enhanced in DX-41
        self.show_main_window()
        self.log_message("Configuration dialog requested")
        
    def show_about_dialog(self):
        """Show about dialog"""
        about_text = f"""DexAgents Modern Windows Agent
Version: {self.config['version']}
Created: {datetime.now().strftime('%Y-%m-%d')}

A comprehensive system monitoring and management agent
for Windows environments.

Features:
• Real-time system monitoring
• WebSocket communication
• System tray integration
• Configurable settings
• Automated status updates

© 2024 DexAgents Team"""
        
        messagebox.showinfo("About DexAgents Agent", about_text)
        
        
    def setup_styles(self):
        """Configure modern styles for the GUI"""
        style = ttk.Style()
        
        # Configure modern theme
        try:
            style.theme_use('clam')
        except:
            pass  # Use default theme if clam is not available
        
        # Configure colors
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Status.TLabel', font=('Arial', 10))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file with defaults"""
        config_file = Path("config.json")
        
        default_config = {
            "server_url": "http://localhost:8080",
            "api_token": "",
            "agent_name": f"agent_{platform.node()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "tags": ["windows", "modern-gui"],
            "auto_start": True,
            "run_as_service": False,
            "minimize_to_tray": True,
            "version": "3.0.0",
            "created_at": datetime.now().isoformat(),
            "update_interval": 30,
            "connection_timeout": 10
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
                    self.logger.info("Configuration loaded successfully")
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")
        
        return default_config
        
    def save_config(self):
        """Save configuration to file"""
        try:
            # Update config with current values
            config_update = {
                "server_url": self.server_url_var.get(),
                "api_token": self.api_token_var.get(),
                "agent_name": self.agent_name_var.get(),
                "tags": [tag.strip() for tag in self.tags_var.get().split(",") if tag.strip()],
                "auto_start": self.auto_start_var.get(),
                "run_as_service": self.run_as_service_var.get(),
                "last_updated": datetime.now().isoformat()
            }
            
            # Add minimize to tray setting if available
            if TRAY_AVAILABLE and hasattr(self, 'minimize_to_tray_var'):
                config_update["minimize_to_tray"] = self.minimize_to_tray_var.get()
                
            # Set default install path if not specified
            if "install_path" not in self.config:
                if platform.system() == "Windows":
                    program_files = os.environ.get("PROGRAMFILES", "C:\\Program Files")
                    config_update["install_path"] = os.path.join(program_files, "DexAgents")
                elif platform.system() == "Darwin":  # macOS
                    config_update["install_path"] = "/Applications/DexAgents"
                else:  # Linux
                    config_update["install_path"] = "/opt/dexagents"
                
            self.config.update(config_update)
            
            # Determine config file path (use Program Files for system-wide install)
            config_file_path = "config.json"
            if self.config.get("install_path"):
                install_path = Path(self.config["install_path"])
                if install_path.exists() or self.config.get("run_as_service", False):
                    # Use system-wide config location for service mode
                    if platform.system() == "Windows":
                        config_dir = Path(os.environ.get("PROGRAMDATA", "C:\\ProgramData")) / "DexAgents"
                    else:
                        config_dir = Path("/etc/dexagents")
                    
                    config_dir.mkdir(parents=True, exist_ok=True)
                    config_file_path = config_dir / "config.json"
            
            with open(config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            # Apply auto-start and service settings
            self.apply_auto_start_settings()
            
            self.logger.info(f"Configuration saved successfully to {config_file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
            return False
            
    def apply_auto_start_settings(self):
        """Apply auto-start and service settings"""
        if not self.service_manager:
            self.logger.warning("Service manager not available, skipping auto-start configuration")
            return
            
        try:
            auto_start_enabled = self.config.get("auto_start", False)
            run_as_service = self.config.get("run_as_service", False)
            
            if auto_start_enabled:
                # Get executable path
                agent_path = self.service_manager.get_executable_path()
                
                # Configure auto-start
                success, message = self.service_manager.configure_auto_start(
                    enable=True,
                    agent_path=agent_path,
                    use_service=run_as_service
                )
                
                if success:
                    self.logger.info(f"Auto-start configured: {message}")
                    self.log_message(f"Auto-start enabled: {message}")
                else:
                    self.logger.warning(f"Auto-start configuration failed: {message}")
                    self.log_message(f"Auto-start warning: {message}")
                    
                    # If service installation failed but auto-start is still wanted,
                    # try fallback to startup entry
                    if run_as_service and not success:
                        self.logger.info("Attempting fallback to startup entry")
                        success, message = self.service_manager.configure_auto_start(
                            enable=True,
                            agent_path=agent_path,
                            use_service=False
                        )
                        if success:
                            self.logger.info(f"Fallback auto-start configured: {message}")
                            self.log_message(f"Auto-start enabled (fallback): {message}")
                            
                            # Update config to reflect that service mode failed
                            self.config["run_as_service"] = False
                            self.run_as_service_var.set(False)
            else:
                # Disable auto-start
                success, message = self.service_manager.configure_auto_start(
                    enable=False,
                    agent_path=""
                )
                
                if success:
                    self.logger.info("Auto-start disabled")
                    self.log_message("Auto-start disabled")
                else:
                    self.logger.warning(f"Failed to disable auto-start: {message}")
                    
        except Exception as e:
            self.logger.error(f"Error applying auto-start settings: {e}")
            self.log_message(f"Auto-start configuration error: {str(e)}")
            
    def load_config_to_gui(self):
        """Load configuration values to GUI elements"""
        try:
            if hasattr(self, 'server_url_var'):
                self.server_url_var.set(self.config.get("server_url", ""))
            if hasattr(self, 'api_token_var'):
                self.api_token_var.set(self.config.get("api_token", ""))
            if hasattr(self, 'agent_name_var'):
                self.agent_name_var.set(self.config.get("agent_name", ""))
            if hasattr(self, 'tags_var'):
                tags = self.config.get("tags", [])
                self.tags_var.set(", ".join(tags) if tags else "")
            if hasattr(self, 'auto_start_var'):
                self.auto_start_var.set(self.config.get("auto_start", True))
            if hasattr(self, 'run_as_service_var'):
                self.run_as_service_var.set(self.config.get("run_as_service", False))
            if hasattr(self, 'minimize_to_tray_var'):
                self.minimize_to_tray_var.set(self.config.get("minimize_to_tray", True))
                
            self.logger.info("Configuration loaded to GUI")
        except Exception as e:
            self.logger.error(f"Error loading config to GUI: {e}")
            
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        
        # Title section
        self.create_title_section(main_frame)
        
        # Configuration section
        self.create_config_section(main_frame)
        
        # Status section
        self.create_status_section(main_frame)
        
        # Control buttons
        self.create_control_buttons(main_frame)
        
        # Log section
        self.create_log_section(main_frame)
        
    def create_title_section(self, parent):
        """Create title section"""
        title_frame = ttk.Frame(parent)
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        title_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(title_frame, text="DexAgents Modern Windows Agent", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2)
        
        # Version info
        version_label = ttk.Label(title_frame, text=f"Version {self.config['version']}", style='Status.TLabel')
        version_label.grid(row=1, column=0, columnspan=2)
        
    def create_config_section(self, parent):
        """Create configuration section"""
        config_frame = ttk.LabelFrame(parent, text="Connection Configuration", padding="10")
        config_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Server URL
        ttk.Label(config_frame, text="Server URL:").grid(row=0, column=0, sticky="w", pady=2)
        self.server_url_var = tk.StringVar(value=self.config.get("server_url", ""))
        self.server_url_entry = ttk.Entry(config_frame, textvariable=self.server_url_var, width=50)
        self.server_url_entry.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # API Token
        ttk.Label(config_frame, text="API Token:").grid(row=1, column=0, sticky="w", pady=2)
        self.api_token_var = tk.StringVar(value=self.config.get("api_token", ""))
        self.api_token_entry = ttk.Entry(config_frame, textvariable=self.api_token_var, width=50, show="*")
        self.api_token_entry.grid(row=1, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Show/Hide token button
        self.show_token_var = tk.BooleanVar()
        self.show_token_check = ttk.Checkbutton(
            config_frame, 
            text="Show Token", 
            variable=self.show_token_var,
            command=self.toggle_token_visibility
        )
        self.show_token_check.grid(row=1, column=2, padx=(5, 0), pady=2)
        
        # Agent Name
        ttk.Label(config_frame, text="Agent Name:").grid(row=2, column=0, sticky="w", pady=2)
        self.agent_name_var = tk.StringVar(value=self.config.get("agent_name", ""))
        self.agent_name_entry = ttk.Entry(config_frame, textvariable=self.agent_name_var, width=50)
        self.agent_name_entry.grid(row=2, column=1, sticky="ew", padx=(10, 0), pady=2)
        
        # Tags
        ttk.Label(config_frame, text="Tags:").grid(row=3, column=0, sticky="w", pady=2)
        self.tags_var = tk.StringVar(value=", ".join(self.config.get("tags", [])))
        self.tags_entry = ttk.Entry(config_frame, textvariable=self.tags_var, width=50)
        self.tags_entry.grid(row=3, column=1, sticky="ew", padx=(10, 0), pady=2)
        ttk.Label(config_frame, text="(comma separated)").grid(row=3, column=2, sticky="w", padx=(5, 0), pady=2)
        
        # Options
        options_frame = ttk.Frame(config_frame)
        options_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        
        self.auto_start_var = tk.BooleanVar(value=self.config.get("auto_start", True))
        self.auto_start_check = ttk.Checkbutton(
            options_frame, 
            text="Auto-start with Windows", 
            variable=self.auto_start_var
        )
        self.auto_start_check.grid(row=0, column=0, sticky="w")
        
        self.run_as_service_var = tk.BooleanVar(value=self.config.get("run_as_service", False))
        self.run_as_service_check = ttk.Checkbutton(
            options_frame, 
            text="Run as Windows Service", 
            variable=self.run_as_service_var
        )
        self.run_as_service_check.grid(row=0, column=1, sticky="w", padx=(20, 0))
        
        # Minimize to tray option (only show if tray is available)
        if TRAY_AVAILABLE:
            self.minimize_to_tray_var = tk.BooleanVar(value=self.config.get("minimize_to_tray", True))
            self.minimize_to_tray_check = ttk.Checkbutton(
                options_frame, 
                text="Minimize to system tray", 
                variable=self.minimize_to_tray_var,
                command=self.on_minimize_to_tray_changed
            )
            self.minimize_to_tray_check.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Advanced Settings button
        if ADVANCED_CONFIG_AVAILABLE:
            self.advanced_button = ttk.Button(
                options_frame,
                text="Advanced Settings...",
                command=self.open_advanced_settings
            )
            self.advanced_button.grid(row=1, column=1, sticky="e", padx=(20, 0), pady=(5, 0))
        
    def create_status_section(self, parent):
        """Create status monitoring section"""
        status_frame = ttk.LabelFrame(parent, text="System Status", padding="10")
        status_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        status_frame.columnconfigure(1, weight=1)
        
        # Connection status
        ttk.Label(status_frame, text="Connection:").grid(row=0, column=0, sticky="w", pady=2)
        self.connection_status = ttk.Label(status_frame, text="Checking...", style='Status.TLabel')
        self.connection_status.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Agent status
        ttk.Label(status_frame, text="Agent:").grid(row=1, column=0, sticky="w", pady=2)
        self.agent_status = ttk.Label(status_frame, text="Stopped", style='Error.TLabel')
        self.agent_status.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Last seen
        ttk.Label(status_frame, text="Last Seen:").grid(row=2, column=0, sticky="w", pady=2)
        self.last_seen_label = ttk.Label(status_frame, text="Never", style='Status.TLabel')
        self.last_seen_label.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # System info
        system_frame = ttk.Frame(status_frame)
        system_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        system_frame.columnconfigure(1, weight=1)
        system_frame.columnconfigure(3, weight=1)
        
        # CPU Usage
        ttk.Label(system_frame, text="CPU:").grid(row=0, column=0, sticky="w", pady=2)
        self.cpu_usage_label = ttk.Label(system_frame, text="0%", style='Status.TLabel')
        self.cpu_usage_label.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Memory Usage
        ttk.Label(system_frame, text="Memory:").grid(row=0, column=2, sticky="w", pady=2)
        self.memory_usage_label = ttk.Label(system_frame, text="0%", style='Status.TLabel')
        self.memory_usage_label.grid(row=0, column=3, sticky="w", padx=(10, 0), pady=2)
        
        # Disk Usage
        ttk.Label(system_frame, text="Disk:").grid(row=1, column=0, sticky="w", pady=2)
        self.disk_usage_label = ttk.Label(system_frame, text="0%", style='Status.TLabel')
        self.disk_usage_label.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=2)
        
        # Auto-start status
        ttk.Label(system_frame, text="Auto-start:").grid(row=1, column=2, sticky="w", pady=2)
        self.auto_start_status_label = ttk.Label(system_frame, text="Unknown", style='Status.TLabel')
        self.auto_start_status_label.grid(row=1, column=3, sticky="w", padx=(10, 0), pady=2)
        
        # Network Status
        ttk.Label(system_frame, text="Network:").grid(row=1, column=2, sticky="w", pady=2)
        self.network_status = ttk.Label(system_frame, text="Unknown", style='Status.TLabel')
        self.network_status.grid(row=1, column=3, sticky="w", padx=(10, 0), pady=2)
        
    def create_control_buttons(self, parent):
        """Create control buttons section"""
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=3, column=0, pady=(0, 10))
        
        # Start/Stop button
        self.start_stop_button = ttk.Button(
            buttons_frame, 
            text="Start Agent", 
            command=self.toggle_agent,
            style='Accent.TButton'
        )
        self.start_stop_button.grid(row=0, column=0, padx=(0, 10))
        
        # Test connection button
        self.test_connection_button = ttk.Button(
            buttons_frame, 
            text="Test Connection", 
            command=self.test_connection_async
        )
        self.test_connection_button.grid(row=0, column=1, padx=(0, 10))
        
        # Save config button
        self.save_config_button = ttk.Button(
            buttons_frame, 
            text="Save Config", 
            command=self.save_configuration
        )
        self.save_config_button.grid(row=0, column=2, padx=(0, 10))
        
        # Open logs button
        self.open_logs_button = ttk.Button(
            buttons_frame, 
            text="Open Logs", 
            command=self.open_logs
        )
        self.open_logs_button.grid(row=0, column=3, padx=(0, 10))
        
        # Open web interface button
        self.open_web_button = ttk.Button(
            buttons_frame, 
            text="Web Interface", 
            command=self.open_web_interface
        )
        self.open_web_button.grid(row=0, column=4)
        
    def create_log_section(self, parent):
        """Create log display section"""
        log_frame = ttk.LabelFrame(parent, text="Activity Log", padding="10")
        log_frame.grid(row=4, column=0, sticky="nsew", pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        parent.rowconfigure(4, weight=1)
        
        # Log text area with scrollbar
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            height=12, 
            width=80,
            font=('Consolas', 9)
        )
        self.log_text.grid(row=0, column=0, sticky="nsew")
        
        # Add initial log message
        self.log_message("Modern DexAgents Windows Agent GUI started")
        
    def toggle_token_visibility(self):
        """Toggle API token visibility"""
        if self.show_token_var.get():
            self.api_token_entry.config(show="")
        else:
            self.api_token_entry.config(show="*")
            
    def on_minimize_to_tray_changed(self):
        """Handle minimize to tray setting change"""
        if hasattr(self, 'minimize_to_tray_var'):
            self.minimize_to_tray = self.minimize_to_tray_var.get()
            
            # Update window close behavior
            if TRAY_AVAILABLE and self.minimize_to_tray:
                self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
            else:
                self.root.protocol("WM_DELETE_WINDOW", self.exit_application)
                
            self.log_message(f"Minimize to tray: {'enabled' if self.minimize_to_tray else 'disabled'}")
            
    def log_message(self, message: str, level: str = "INFO"):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        # Add to GUI log
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # Limit log size
        if self.log_text.index(tk.END).split('.')[0] > '1000':
            self.log_text.delete('1.0', '100.0')
        
        # Log to file
        self.logger.info(message)
        
    def get_system_info(self) -> Optional[Dict[str, Any]]:
        """Get comprehensive system information"""
        try:
            # Basic system info
            hostname = platform.node()
            os_info = platform.platform()
            python_version = platform.python_version()
            
            # Performance metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Disk usage
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.device] = {
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100
                    }
                except PermissionError:
                    continue
            
            # Network info
            network_info = {}
            try:
                net_io = psutil.net_io_counters()
                network_info = {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                }
            except Exception as e:
                self.logger.warning(f"Could not get network info: {e}")
            
            return {
                "hostname": hostname,
                "os_info": os_info,
                "python_version": python_version,
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "memory_total": memory.total,
                "memory_available": memory.available,
                "disk_usage": disk_usage,
                "network_info": network_info,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return None
            
    def test_connection_async(self):
        """Test connection to server asynchronously"""
        def test_connection():
            try:
                server_url = self.server_url_var.get().strip()
                api_token = self.api_token_var.get().strip()
                
                if not server_url:
                    self.status_queue.put(("connection", "No server URL", "error"))
                    return
                
                if not api_token:
                    self.status_queue.put(("connection", "No API token", "error"))
                    return
                
                # Test basic connectivity
                try:
                    response = requests.get(
                        server_url, 
                        timeout=self.config.get("connection_timeout", 10),
                        headers={"Authorization": f"Bearer {api_token}"}
                    )
                    
                    if response.status_code == 200:
                        self.status_queue.put(("connection", "Connected", "success"))
                        self.log_message("Connection test successful")
                        # Update tray status
                        if self.tray_manager:
                            self.tray_manager.update_status("connected")
                    else:
                        self.status_queue.put(("connection", f"Failed ({response.status_code})", "error"))
                        self.log_message(f"Connection test failed: {response.status_code}")
                        # Update tray status
                        if self.tray_manager:
                            self.tray_manager.update_status("error")
                        
                except requests.exceptions.ConnectionError:
                    self.status_queue.put(("connection", "Connection refused", "error"))
                    self.log_message("Connection refused - server may be down")
                    # Update tray status
                    if self.tray_manager:
                        self.tray_manager.update_status("disconnected")
                except requests.exceptions.Timeout:
                    self.status_queue.put(("connection", "Timeout", "error"))
                    self.log_message("Connection timeout")
                    # Update tray status
                    if self.tray_manager:
                        self.tray_manager.update_status("error")
                except Exception as e:
                    self.status_queue.put(("connection", f"Error: {str(e)}", "error"))
                    self.log_message(f"Connection error: {e}")
                    # Update tray status
                    if self.tray_manager:
                        self.tray_manager.update_status("error")
                    
            except Exception as e:
                self.log_message(f"Test connection error: {e}")
                self.status_queue.put(("connection", "Error", "error"))
        
        # Run in background thread
        threading.Thread(target=test_connection, daemon=True).start()
        
    def register_agent(self) -> bool:
        """Register agent with server"""
        try:
            system_info = self.get_system_info()
            if not system_info:
                return False
                
            agent_data = {
                "hostname": system_info["hostname"],
                "os_info": system_info["os_info"],
                "python_version": system_info["python_version"],
                "version": self.config["version"],
                "status": "online",
                "last_seen": datetime.now().isoformat(),
                "tags": self.config["tags"],
                "system_info": system_info
            }
            
            server_url = self.server_url_var.get().strip()
            api_token = self.api_token_var.get().strip()
            
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                f"{server_url}/api/v1/agents/register", 
                json=agent_data, 
                headers=headers,
                timeout=self.config.get("connection_timeout", 10)
            )
            
            if response.status_code == 200:
                agent_info = response.json()
                self.agent_id = agent_info.get("id")
                self.log_message(f"Agent registered successfully with ID: {self.agent_id}")
                return True
            else:
                self.log_message(f"Failed to register agent: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_message(f"Error registering agent: {e}")
            return False
            
    def update_status(self) -> bool:
        """Update agent status with server"""
        try:
            if not self.agent_id:
                self.log_message("No agent ID - skipping status update")
                return False
                
            system_info = self.get_system_info()
            if not system_info:
                return False
                
            update_data = {
                "status": "online",
                "last_seen": datetime.now().isoformat(),
                "system_info": system_info
            }
            
            server_url = self.server_url_var.get().strip()
            api_token = self.api_token_var.get().strip()
            
            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.put(
                f"{server_url}/api/v1/agents/{self.agent_id}", 
                json=update_data, 
                headers=headers,
                timeout=self.config.get("connection_timeout", 10)
            )
            
            return response.status_code == 200
            
        except Exception as e:
            self.log_message(f"Error updating status: {e}")
            return False
            
    def agent_loop(self):
        """Main agent loop"""
        self.log_message("Starting agent loop")
        
        # Initial registration
        if not self.register_agent():
            self.log_message("Failed to register agent - stopping")
            self.agent_running = False
            # Update tray status
            if self.tray_manager:
                self.tray_manager.update_status("error", "Registration failed")
            return
        else:
            # Registration successful
            if self.tray_manager:
                self.tray_manager.update_status("connected", "Registered successfully")
            
            # Setup and start WebSocket connection after successful registration
            if WEBSOCKET_AVAILABLE:
                self.setup_websocket_client()  # Re-setup with correct agent_id
                if self.websocket_client:
                    self.start_websocket_connection()
            
        update_interval = self.config.get("update_interval", 30)
        
        while self.agent_running:
            try:
                # Update status
                if self.update_status():
                    current_time = datetime.now().strftime("%H:%M:%S")
                    self.status_queue.put(("last_seen", current_time, "success"))
                    # Update tray with successful status
                    if self.tray_manager:
                        self.tray_manager.update_status("connected", current_time)
                else:
                    self.log_message("Failed to update status")
                    # Update tray with error status
                    if self.tray_manager:
                        self.tray_manager.update_status("error", "Update failed")
                    
                time.sleep(update_interval)
                
            except Exception as e:
                self.log_message(f"Error in agent loop: {e}")
                time.sleep(60)  # Wait before retry
                
        self.log_message("Agent loop stopped")
        
    def toggle_agent(self):
        """Start or stop agent"""
        if not self.agent_running:
            # Validate configuration
            if not self.server_url_var.get().strip():
                messagebox.showerror("Error", "Please enter server URL")
                return
                
            if not self.api_token_var.get().strip():
                messagebox.showerror("Error", "Please enter API token")
                return
            
            # Start agent
            self.agent_running = True
            self.agent_status.config(text="Running", style='Success.TLabel')
            self.start_stop_button.config(text="Stop Agent")
            self.log_message("Starting agent...")
            
            # Update tray status
            if self.tray_manager:
                self.tray_manager.update_status("disconnected", "Starting...")
                self.tray_manager.show_notification(
                    "DexAgents Agent", 
                    "Agent is starting up..."
                )
            
            # Start agent thread
            self.agent_thread = threading.Thread(target=self.agent_loop, daemon=True)
            self.agent_thread.start()
        else:
            # Stop agent
            self.agent_running = False
            self.agent_status.config(text="Stopped", style='Error.TLabel')
            self.start_stop_button.config(text="Start Agent")
            self.log_message("Stopping agent...")
            
            # Update tray status
            if self.tray_manager:
                self.tray_manager.update_status("disconnected", "Stopped")
                self.tray_manager.show_notification(
                    "DexAgents Agent", 
                    "Agent has been stopped"
                )
            
    def save_configuration(self):
        """Save current configuration"""
        if self.save_config():
            self.log_message("Configuration saved successfully")
            messagebox.showinfo("Success", "Configuration saved successfully!")
        else:
            messagebox.showerror("Error", "Failed to save configuration")
            
    def open_logs(self):
        """Open logs directory"""
        try:
            log_dir = Path("logs")
            if log_dir.exists():
                os.startfile(log_dir)
            else:
                messagebox.showinfo("Info", "Logs directory not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open logs: {e}")
            
    def open_web_interface(self):
        """Open web interface"""
        try:
            server_url = self.server_url_var.get().strip()
            if server_url:
                # Replace backend port with frontend port
                web_url = server_url.replace(":8000", ":3000")
                webbrowser.open(web_url)
            else:
                messagebox.showinfo("Info", "Please enter server URL first")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open web interface: {e}")
            
    def setup_status_updates(self):
        """Setup periodic status updates"""
        def update_status_display():
            try:
                # Update system info
                system_info = self.get_system_info()
                if system_info:
                    self.cpu_usage_label.config(text=f"{system_info['cpu_usage']:.1f}%")
                    self.memory_usage_label.config(text=f"{system_info['memory_usage']:.1f}%")
                    
                    # Get disk usage for C: drive
                    disk_usage = system_info.get('disk_usage', {})
                    c_drive_usage = disk_usage.get('C:\\', {}).get('percent', 0)
                    self.disk_usage_label.config(text=f"{c_drive_usage:.1f}%")
                
                # Update auto-start status
                if self.service_manager:
                    auto_start_status = self.service_manager.get_auto_start_status()
                    if auto_start_status["enabled"]:
                        if auto_start_status["service"]["running"]:
                            status_text = "Service"
                            style = 'Success.TLabel'
                        else:
                            status_text = "Enabled"
                            style = 'Success.TLabel'
                    else:
                        status_text = "Disabled"
                        style = 'Error.TLabel'
                    
                    self.auto_start_status_label.config(text=status_text, style=style)
                
                # Check status queue
                try:
                    while True:
                        queue_item = self.status_queue.get_nowait()
                        
                        # Handle both 2-tuple and 3-tuple formats
                        if len(queue_item) == 2:
                            status_type, value = queue_item
                            style = "info"
                        else:
                            status_type, value, style = queue_item
                        
                        if status_type == "connection":
                            if style == "success":
                                self.connection_status.config(text=value, style='Success.TLabel')
                            elif style == "error":
                                self.connection_status.config(text=value, style='Error.TLabel')
                            else:
                                self.connection_status.config(text=value, style='Status.TLabel')
                        elif status_type == "last_seen":
                            self.last_seen_label.config(text=value)
                            
                except queue.Empty:
                    pass
                    
            except Exception as e:
                self.logger.error(f"Error updating status display: {e}")
                
            # Schedule next update
            self.root.after(5000, update_status_display)
            
        # Start status updates
        update_status_display()
        
    def open_advanced_settings(self):
        """Open advanced configuration dialog"""
        if not ADVANCED_CONFIG_AVAILABLE:
            messagebox.showerror("Error", "Advanced configuration dialog is not available")
            return
            
        try:
            # Create and show advanced config dialog
            dialog = AdvancedConfigDialog(self.root, self.config, self.logger)
            self.root.wait_window(dialog.dialog)
            
            result = dialog.get_result()
            if result:
                # Update configuration with advanced settings
                self.config.update(result)
                
                # Save updated configuration
                if self.save_config():
                    messagebox.showinfo("Success", "Advanced settings saved successfully!")
                    self.logger.info("Advanced settings applied and saved")
                else:
                    messagebox.showerror("Error", "Failed to save advanced settings")
            else:
                self.logger.info("Advanced settings dialog cancelled")
                
        except Exception as e:
            self.logger.error(f"Error opening advanced settings: {e}")
            messagebox.showerror("Error", f"Failed to open advanced settings: {str(e)}")
    
    def save_and_validate_config(self):
        """Save configuration with validation"""
        try:
            # Validate required fields
            if not self.server_url_var.get().strip():
                messagebox.showerror("Validation Error", "Server URL is required")
                return False
                
            if not self.api_token_var.get().strip():
                messagebox.showerror("Validation Error", "API Token is required")
                return False
                
            if not self.agent_name_var.get().strip():
                messagebox.showerror("Validation Error", "Agent Name is required")
                return False
            
            # Save configuration
            if self.save_config():
                messagebox.showinfo("Success", "Configuration saved successfully!")
                return True
            else:
                messagebox.showerror("Error", "Failed to save configuration")
                return False
                
        except Exception as e:
            self.logger.error(f"Error validating/saving config: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            return False
    
    def run(self):
        """Run the GUI application"""
        try:
            self.log_message("GUI application started")
            
            # Handle start minimized
            if self.start_minimized and self.tray_manager:
                self.root.withdraw()  # Hide window
                self.tray_manager.show_notification("DexAgents", "Started minimized to tray")
            
            self.root.mainloop()
        except Exception as e:
            self.logger.error(f"GUI error: {e}")
        finally:
            self.logger.info("GUI application stopped")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DexAgents Windows Agent")
    parser.add_argument("--service-mode", action="store_true", 
                       help="Run in service mode (headless)")
    parser.add_argument("--minimized", action="store_true",
                       help="Start minimized to system tray")
    parser.add_argument("--config", type=str,
                       help="Path to configuration file")
    
    args = parser.parse_args()
    
    try:
        if args.service_mode:
            # Run in service mode (headless)
            from windows_agent import DexWindowsAgent
            
            config_path = args.config or "config.json"
            agent = DexWindowsAgent(config_path)
            agent.run()
        else:
            # Run with GUI
            app = ModernDexAgentGUI()
            
            # Apply startup arguments
            if args.minimized and app.tray_manager:
                app.start_minimized = True
                
            if args.config:
                # Load specified config file
                try:
                    with open(args.config, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        app.config.update(config)
                        app.load_config_to_gui()
                except Exception as e:
                    app.logger.error(f"Failed to load config file {args.config}: {e}")
            
            app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 