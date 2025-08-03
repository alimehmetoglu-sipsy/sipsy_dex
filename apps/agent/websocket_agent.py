#!/usr/bin/env python3
"""
WebSocket-based DexAgents Agent
Connects to backend via WebSocket and executes PowerShell commands
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
import argparse

# Create logs directory
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/websocket_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WebSocketAgent:
    def __init__(self, agent_id: str, server_url: str = "ws://localhost:8080", api_token: str = "dev-secret-key"):
        self.agent_id = agent_id
        self.server_url = server_url
        self.api_token = api_token
        self.websocket = None
        self.running = False
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system information"""
        try:
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_usage = {}
            
            # Get disk usage for all mounted drives
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
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {}
    
    async def execute_powershell_command(self, command: str, timeout: int = 30, working_directory: Optional[str] = None) -> Dict[str, Any]:
        """Execute PowerShell command and return result"""
        try:
            logger.info(f"Executing command: {command}")
            
            # Prepare command for different platforms
            if platform.system() == "Windows":
                cmd = ["powershell", "-Command", command]
            else:
                # For Linux/Mac, use bash or sh
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
                
                logger.info(f"Command executed successfully: exit_code={process.returncode}")
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
                # Execute command
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
            "agent_id": self.agent_id,
            "system_info": system_info,
            "status": "online"
        })
    
    async def register_agent(self):
        """Register agent with server"""
        system_info = self.get_system_info()
        
        registration_data = {
            "agent_id": self.agent_id,
            "hostname": system_info.get("hostname", socket.gethostname()),
            "ip": socket.gethostbyname(socket.gethostname()),
            "os": platform.system(),
            "version": platform.version(),
            "status": "online",
            "tags": ["websocket-agent", "powershell"],
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
        ws_url = f"{self.server_url}/api/v1/ws/{self.agent_id}"
        logger.info(f"Connecting to: {ws_url}")
        
        try:
            # Create connection with headers
            headers = {"Authorization": f"Bearer {self.api_token}"}
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
    
    async def run(self):
        """Run agent with reconnection logic"""
        while True:
            try:
                await self.connect_and_run()
                logger.info("Connection closed, attempting to reconnect in 10 seconds...")
                await asyncio.sleep(10)
                
            except KeyboardInterrupt:
                logger.info("Agent stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                logger.info("Retrying in 30 seconds...")
                await asyncio.sleep(30)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="DexAgents WebSocket Agent")
    parser.add_argument("--agent-id", required=True, help="Agent ID")
    parser.add_argument("--server-url", default="ws://localhost:8080", help="WebSocket server URL")
    parser.add_argument("--api-token", default="dev-secret-key", help="API Token")
    
    args = parser.parse_args()
    
    # Create agent
    agent = WebSocketAgent(
        agent_id=args.agent_id,
        server_url=args.server_url,
        api_token=args.api_token
    )
    
    try:
        # Run agent
        asyncio.run(agent.run())
    except KeyboardInterrupt:
        logger.info("Shutting down WebSocket agent...")

if __name__ == "__main__":
    main()