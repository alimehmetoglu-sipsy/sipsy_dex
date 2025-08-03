#!/usr/bin/env python3
"""
Windows DexAgents Agent - Standalone executable for Windows
Connects to DexAgents backend and executes PowerShell commands
"""

import asyncio
import websockets
import json
import logging
import platform
import socket
import psutil
import subprocess
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional
import tkinter as tk
from tkinter import messagebox
import threading
import time

# Create logs directory
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/dexagents_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DexAgentsWindowsAgent:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
        self.running = False
        self.websocket = None
        self.gui_running = False
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "server_url": "ws://localhost:8080",
            "api_token": "test-token",
            "agent_name": f"WindowsAgent_{platform.node()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "tags": ["windows", "powershell"],
            "auto_start": True,
            "run_as_service": False
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
                    logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                
        return default_config
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get Windows system information"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_usage = {}
            
            # Get disk usage for Windows drives
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = round((usage.used / usage.total) * 100, 1)
                except PermissionError:
                    continue
            
            return {
                "hostname": platform.node(),
                "os_version": platform.platform(),
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "disk_usage": disk_usage,
                "timestamp": datetime.now().isoformat(),
                "python_version": platform.python_version(),
                "agent_version": "1.0.0"
            }
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {}
    
    async def execute_powershell_command(self, command: str, timeout: int = 30, working_directory: Optional[str] = None) -> Dict[str, Any]:
        """Execute PowerShell command on Windows"""
        try:
            logger.info(f"Executing PowerShell command: {command}")
            
            # Prepare PowerShell command
            if platform.system() == "Windows":
                cmd = ["powershell", "-Command", command]
            else:
                # Fallback for testing on non-Windows
                cmd = ["bash", "-c", command]
            
            # Set working directory if provided
            cwd = working_directory if working_directory else None
            
            # Execute command
            start_time = datetime.now()
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                execution_time = (datetime.now() - start_time).total_seconds()
                
                result = {
                    "command": command,
                    "success": process.returncode == 0,
                    "output": stdout.decode('utf-8', errors='ignore') if stdout else "",
                    "error": stderr.decode('utf-8', errors='ignore') if stderr else "",
                    "exit_code": process.returncode,
                    "execution_time": execution_time
                }
                
                logger.info(f"Command executed: exit_code={process.returncode}, time={execution_time:.3f}s")
                return result
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "command": command,
                    "success": False,
                    "output": "",
                    "error": f"Command timed out after {timeout} seconds",
                    "exit_code": -1,
                    "execution_time": timeout
                }
                
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return {
                "command": command,
                "success": False,
                "output": "",
                "error": str(e),
                "exit_code": -1,
                "execution_time": 0
            }
    
    async def send_message(self, message_type: str, data: Dict[str, Any]):
        """Send message to server via WebSocket"""
        if not self.websocket:
            logger.error("WebSocket not connected")
            return
            
        try:
            message = {
                "type": message_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            await self.websocket.send(json.dumps(message))
            logger.debug(f"Sent message: {message_type}")
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
    
    async def handle_message(self, message: str):
        """Handle incoming message from server"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            message_data = data.get("data", {})
            
            logger.info(f"Received message: {message_type}")
            
            if message_type == "command":
                # Execute PowerShell command
                command = message_data.get("command")
                command_id = message_data.get("command_id")
                timeout = message_data.get("timeout", 30)
                working_directory = message_data.get("working_directory")
                
                if command and command_id:
                    result = await self.execute_powershell_command(
                        command, timeout, working_directory
                    )
                    
                    # Send result back
                    await self.send_message("command_result", {
                        "command_id": command_id,
                        "result": result
                    })
                else:
                    logger.error("Invalid command message format")
            
            elif message_type == "ping":
                # Respond to ping with pong
                await self.send_message("pong", {"timestamp": datetime.now().isoformat()})
            
            elif message_type == "welcome":
                logger.info("Received welcome message from server")
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON message: {str(e)}")
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
    
    async def send_heartbeat(self):
        """Send heartbeat with system info"""
        system_info = self.get_system_info()
        await self.send_message("heartbeat", {
            "agent_id": self.config["agent_name"],
            "system_info": system_info,
            "status": "online"
        })
    
    async def register_agent(self):
        """Register agent with server"""
        system_info = self.get_system_info()
        
        registration_data = {
            "agent_id": self.config["agent_name"],
            "hostname": system_info.get("hostname", socket.gethostname()),
            "ip": socket.gethostbyname(socket.gethostname()),
            "os": platform.system(),
            "version": system_info.get("agent_version", "1.0.0"),
            "status": "online",
            "tags": self.config["tags"],
            "system_info": system_info
        }
        
        await self.send_message("register", registration_data)
        logger.info("Agent registration sent")
    
    async def heartbeat_loop(self):
        """Periodic heartbeat loop"""
        while self.running:
            try:
                await self.send_heartbeat()
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {str(e)}")
                await asyncio.sleep(30)
    
    async def connect_and_run(self):
        """Main connection loop"""
        ws_url = f"{self.config['server_url']}/api/v1/ws/{self.config['agent_name']}"
        logger.info(f"Connecting to: {ws_url}")
        
        try:
            # Create connection with headers
            headers = {"Authorization": f"Bearer {self.config['api_token']}"}
            async with websockets.connect(
                ws_url,
                additional_headers=headers,
                ping_interval=20,
                ping_timeout=10
            ) as websocket:
                self.websocket = websocket
                self.running = True
                
                logger.info("WebSocket connected successfully")
                
                # Register agent
                await self.register_agent()
                
                # Start heartbeat loop
                heartbeat_task = asyncio.create_task(self.heartbeat_loop())
                
                try:
                    # Listen for messages
                    async for message in websocket:
                        await self.handle_message(message)
                        
                except websockets.exceptions.ConnectionClosed:
                    logger.info("WebSocket connection closed")
                finally:
                    self.running = False
                    heartbeat_task.cancel()
                    try:
                        await heartbeat_task
                    except asyncio.CancelledError:
                        pass
                    
        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}")
            raise
    
    async def run_agent(self):
        """Run agent with reconnection logic"""
        while self.running:
            try:
                await self.connect_and_run()
                if self.running:
                    logger.info("Connection lost, attempting to reconnect in 10 seconds...")
                    await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Agent error: {str(e)}")
                if self.running:
                    logger.info("Retrying in 30 seconds...")
                    await asyncio.sleep(30)
    
    def create_gui(self):
        """Create simple GUI for Windows agent"""
        root = tk.Tk()
        root.title("DexAgents Windows Agent")
        root.geometry("400x300")
        
        # Status label
        status_label = tk.Label(root, text="Status: Stopped", font=("Arial", 12))
        status_label.pack(pady=10)
        
        # Info label
        info_label = tk.Label(root, text=f"Agent: {self.config['agent_name']}", font=("Arial", 10))
        info_label.pack(pady=5)
        
        server_label = tk.Label(root, text=f"Server: {self.config['server_url']}", font=("Arial", 10))
        server_label.pack(pady=5)
        
        # Start/Stop button
        def toggle_agent():
            if not self.running:
                self.running = True
                status_label.config(text="Status: Starting...")
                start_button.config(text="Stop Agent")
                
                # Start agent in separate thread
                def run_agent_thread():
                    try:
                        asyncio.run(self.run_agent())
                    except Exception as e:
                        logger.error(f"Agent thread error: {e}")
                        self.running = False
                        root.after(0, lambda: [
                            status_label.config(text="Status: Error"),
                            start_button.config(text="Start Agent")
                        ])
                
                threading.Thread(target=run_agent_thread, daemon=True).start()
                status_label.config(text="Status: Running")
            else:
                self.running = False
                status_label.config(text="Status: Stopping...")
                start_button.config(text="Start Agent")
                root.after(1000, lambda: status_label.config(text="Status: Stopped"))
        
        start_button = tk.Button(root, text="Start Agent", command=toggle_agent, font=("Arial", 12))
        start_button.pack(pady=20)
        
        # Exit button
        def on_exit():
            self.running = False
            root.quit()
            
        exit_button = tk.Button(root, text="Exit", command=on_exit, font=("Arial", 10))
        exit_button.pack(pady=10)
        
        # Handle window close
        root.protocol("WM_DELETE_WINDOW", on_exit)
        
        self.gui_running = True
        root.mainloop()
        self.gui_running = False

def main():
    """Main entry point"""
    logger.info("Starting DexAgents Windows Agent")
    
    agent = DexAgentsWindowsAgent()
    
    # Check if running with GUI or console
    if len(sys.argv) > 1 and sys.argv[1] == "--console":
        # Console mode
        try:
            asyncio.run(agent.run_agent())
        except KeyboardInterrupt:
            logger.info("Agent stopped by user")
    else:
        # GUI mode (default for Windows)
        try:
            agent.create_gui()
        except Exception as e:
            logger.error(f"GUI error: {e}")
            # Fallback to console mode
            try:
                asyncio.run(agent.run_agent())
            except KeyboardInterrupt:
                logger.info("Agent stopped by user")

if __name__ == "__main__":
    main()