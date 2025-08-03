import os
import zipfile
import tempfile
import logging
from typing import Optional
from ..schemas.agent import AgentInstallerConfig

logger = logging.getLogger(__name__)

class PythonAgentService:
    @staticmethod
    def create_python_agent(config: AgentInstallerConfig) -> str:
        """Create a simplified Python agent package"""
        try:
            # Create temporary directory for agent files
            temp_dir = tempfile.mkdtemp(prefix="python_agent_")
            
            # Agent configuration
            agent_name = config.agent_name or "DexAgent"
            server_url = config.server_url or "http://localhost:8080"
            api_token = config.api_token or "your-secret-key-here"
            
            # Create main agent file
            agent_code = PythonAgentService._generate_agent_code(
                agent_name, server_url, api_token, config.tags or []
            )
            
            # Create requirements file
            requirements = PythonAgentService._generate_requirements()
            
            # Create batch launcher
            launcher_bat = PythonAgentService._generate_launcher_bat(agent_name)
            
            # Create installation script
            install_bat = PythonAgentService._generate_install_bat()
            
            # Create README
            readme = PythonAgentService._generate_readme(agent_name, server_url)
            
            # Write files to temp directory
            agent_file = os.path.join(temp_dir, "agent.py")
            with open(agent_file, 'w', encoding='utf-8') as f:
                f.write(agent_code)
            
            req_file = os.path.join(temp_dir, "requirements.txt")
            with open(req_file, 'w', encoding='utf-8') as f:
                f.write(requirements)
            
            launcher_file = os.path.join(temp_dir, f"start_{agent_name.lower()}.bat")
            with open(launcher_file, 'w', encoding='utf-8') as f:
                f.write(launcher_bat)
            
            install_file = os.path.join(temp_dir, "install.bat")
            with open(install_file, 'w', encoding='utf-8') as f:
                f.write(install_bat)
            
            readme_file = os.path.join(temp_dir, "README.md")
            with open(readme_file, 'w', encoding='utf-8') as f:
                f.write(readme)
            
            # Create zip file
            zip_path = os.path.join(temp_dir, f"DexAgent_{agent_name}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(agent_file, "agent.py")
                zipf.write(req_file, "requirements.txt")
                zipf.write(launcher_file, f"start_{agent_name.lower()}.bat")
                zipf.write(install_file, "install.bat")
                zipf.write(readme_file, "README.md")
            
            logger.info(f"Created Python agent package: {zip_path}")
            return zip_path
            
        except Exception as e:
            logger.error(f"Error creating Python agent: {str(e)}")
            raise

    @staticmethod
    def _generate_agent_code(agent_name: str, server_url: str, api_token: str, tags: list) -> str:
        """Generate the main agent Python code"""
        return f'''#!/usr/bin/env python3
"""
DexAgent - Python Agent for Windows
Agent Name: {agent_name}
Server: {server_url}
"""

import asyncio
import websockets
import json
import subprocess
import platform
import psutil
import socket
import time
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DexAgent:
    def __init__(self):
        self.agent_name = "{agent_name}"
        self.server_url = "{server_url}"
        self.api_token = "{api_token}"
        self.tags = {tags}
        self.websocket = None
        self.running = False
        self.heartbeat_interval = 30
        
        # Agent info - use consistent ID based on hostname and agent name
        hostname = socket.gethostname()
        # Create stable agent ID from hostname and agent name
        agent_id = f"{{hostname}}-{{self.agent_name}}".replace(" ", "_").lower()
        
        self.agent_info = {{
            "id": agent_id, 
            "name": self.agent_name,
            "hostname": hostname,
            "platform": platform.system(),
            "version": "2.0.0",
            "tags": self.tags,
            "status": "online",
            "last_seen": datetime.now().isoformat(),
            "system_info": self._get_system_info()
        }}
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information"""
        try:
            return self._get_system_info_fallback()
        except Exception as e:
            logger.error(f"Error getting system info: {{e}}")
            return {{}}
    
    def _get_system_info_fallback(self) -> Dict[str, Any]:
        """Fallback method using psutil if PowerShell fails"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            disk_usage = {{}}
            for partition in psutil.disk_partitions():
                if partition.fstype:
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_usage[partition.device.replace('\\\\', '')] = round(usage.percent, 1)
                    except PermissionError:
                        continue
            
            return {{
                "cpu_usage": cpu_percent,
                "cpu_percent": cpu_percent,
                "memory_usage": memory.percent,
                "memory_percent": memory.percent,
                "disk_usage": disk_usage,
                "uptime": time.time() - psutil.boot_time(),
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "architecture": platform.architecture()[0],
                "cpu_count": psutil.cpu_count(),
                "total_memory": memory.total,
                "available_memory": memory.available,
                "process_count": len(psutil.pids())
            }}
        except Exception as e:
            logger.error(f"Error in fallback system info: {{e}}")
            return {{}}
    
    async def connect(self):
        """Connect to the server via WebSocket"""
        ws_url = self.server_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{{ws_url}}/api/v1/ws/agent"
        
        try:
            logger.info(f"Connecting to {{ws_url}}")
            # Try with additional_headers first (newer versions), fallback without headers
            try:
                self.websocket = await websockets.connect(
                    ws_url,
                    additional_headers={{"Authorization": f"Bearer {{self.api_token}}"}}
                )
            except TypeError:
                # Fallback for older websockets versions - connect without auth headers
                logger.warning("Using older websockets version - connecting without auth headers")
                self.websocket = await websockets.connect(ws_url)
            
            # Register agent
            await self._register_agent()
            
            self.running = True
            logger.info(f"Agent {{self.agent_name}} connected successfully")
            
            # Start heartbeat and message handling
            await asyncio.gather(
                self._heartbeat_loop(),
                self._message_handler()
            )
            
        except Exception as e:
            logger.error(f"Connection error: {{e}}")
            await asyncio.sleep(5)
            await self.connect()  # Retry connection
    
    async def _register_agent(self):
        """Register this agent with the server"""
        register_msg = {{
            "type": "register",
            "data": self.agent_info
        }}
        await self.websocket.send(json.dumps(register_msg))
        logger.info("Agent registration sent")
    
    async def _heartbeat_loop(self):
        """Send periodic heartbeat messages"""
        while self.running:
            try:
                if self.websocket:
                    heartbeat_msg = {{
                        "type": "heartbeat",
                        "data": {{
                            "agent_id": self.agent_info["id"],
                            "timestamp": datetime.now().isoformat(),
                            "system_info": self._get_system_info()
                        }}
                    }}
                    await self.websocket.send(json.dumps(heartbeat_msg))
                    logger.debug("Heartbeat sent")
                
                await asyncio.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat error: {{e}}")
                break
    
    async def _message_handler(self):
        """Handle incoming messages from server"""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._process_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {{e}}")
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
        except Exception as e:
            logger.error(f"Message handler error: {{e}}")
    
    async def _process_message(self, data: Dict[str, Any]):
        """Process incoming command from server"""
        message_type = data.get("type")
        
        logger.info(f"Processing message type: {{message_type}}")
        
        if message_type == "command":
            await self._execute_command(data.get("data", {{}}))
        elif message_type == "ping":
            await self._send_pong()
        elif message_type == "system_info_request":
            await self._send_system_info_update()
        elif message_type == "powershell_command":
            logger.info("Received PowerShell command via WebSocket")
            await self._execute_powershell_json(data)
        else:
            logger.warning(f"Unknown message type: {{message_type}}")
    
    async def _execute_command(self, command_data: Dict[str, Any]):
        """Execute a command received from server"""
        try:
            command_id = command_data.get("id")
            command_type = command_data.get("type", "powershell")
            command_text = command_data.get("command", "")
            
            logger.info(f"Executing command {{command_id}}: {{command_text[:100]}}")
            
            # Execute command based on type
            if command_type == "powershell":
                result = await self._execute_powershell(command_text)
            elif command_type == "cmd":
                result = await self._execute_cmd(command_text)
            else:
                result = {{
                    "success": False,
                    "output": f"Unsupported command type: {{command_type}}",
                    "error": "Invalid command type"
                }}
            
            # Send result back to server
            response = {{
                "type": "command_result",
                "data": {{
                    "command_id": command_id,
                    "agent_id": self.agent_info["id"],
                    "timestamp": datetime.now().isoformat(),
                    **result
                }}
            }}
            
            await self.websocket.send(json.dumps(response))
            logger.info(f"Command {{command_id}} result sent")
            
        except Exception as e:
            logger.error(f"Error executing command: {{e}}")
            
            # Send error response
            if self.websocket:
                error_response = {{
                    "type": "command_result",
                    "data": {{
                        "command_id": command_data.get("id"),
                        "agent_id": self.agent_info["id"],
                        "timestamp": datetime.now().isoformat(),
                        "success": False,
                        "output": "",
                        "error": str(e)
                    }}
                }}
                await self.websocket.send(json.dumps(error_response))
    
    async def _execute_powershell(self, command: str) -> Dict[str, Any]:
        """Execute PowerShell command"""
        try:
            logger.info(f"Executing PowerShell command: {{command[:100]}}...")
            
            process = await asyncio.create_subprocess_exec(
                "powershell.exe", "-Command", command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            result = {{
                "success": process.returncode == 0,
                "output": stdout.decode('utf-8', errors='ignore'),
                "error": stderr.decode('utf-8', errors='ignore'),
                "return_code": process.returncode
            }}
            
            logger.info(f"PowerShell command finished with return code: {{process.returncode}}")
            if not result["success"]:
                logger.error(f"PowerShell error: {{result['error']}}")
            
            return result
        except Exception as e:
            logger.error(f"Exception executing PowerShell: {{str(e)}}")
            return {{
                "success": False,
                "output": "",
                "error": str(e),
                "return_code": -1
            }}
    
    async def _execute_cmd(self, command: str) -> Dict[str, Any]:
        """Execute CMD command"""
        try:
            process = await asyncio.create_subprocess_exec(
                "cmd.exe", "/c", command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {{
                "success": process.returncode == 0,
                "output": stdout.decode('utf-8', errors='ignore'),
                "error": stderr.decode('utf-8', errors='ignore'),
                "return_code": process.returncode
            }}
        except Exception as e:
            return {{
                "success": False,
                "output": "",
                "error": str(e),
                "return_code": -1
            }}
    
    async def _send_pong(self):
        """Send pong response to ping"""
        pong_msg = {{
            "type": "pong",
            "data": {{
                "agent_id": self.agent_info["id"],
                "timestamp": datetime.now().isoformat()
            }}
        }}
        await self.websocket.send(json.dumps(pong_msg))
    
    async def _send_system_info_update(self):
        """Send current system information to server"""
        try:
            # Get fresh system information via PowerShell
            system_info = self._get_system_info()
            
            # Send system info update message
            update_msg = {{
                "type": "system_info_update",
                "data": system_info,
                "timestamp": datetime.now().isoformat()
            }}
            
            await self.websocket.send(json.dumps(update_msg))
            logger.info("System info update sent to server")
            
        except Exception as e:
            logger.error(f"Error sending system info update: {{e}}")
    
    def _get_network_info(self) -> Dict[str, Any]:
        """Get network interface information"""
        try:
            network_info = {{}}
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:  # IPv4
                        network_info[interface] = {{
                            "ip": addr.address,
                            "netmask": addr.netmask
                        }}
                        break
            return network_info
        except Exception as e:
            logger.error(f"Error getting network info: {{e}}")
            return {{}}
    
    async def _execute_powershell_json(self, message_data: Dict[str, Any]):
        """Execute PowerShell command and return JSON response"""
        try:
            request_id = message_data.get("request_id")
            command = message_data.get("command", "")
            response_type = message_data.get("response_type", "powershell_result")
            
            logger.info(f"Executing PowerShell JSON command for request {{request_id}}")
            
            # Execute PowerShell command
            result = await self._execute_powershell(command)
            
            if result['success'] and result['output']:
                try:
                    # Try to parse JSON output
                    json_data = json.loads(result['output'])
                    
                    # Send response based on response_type
                    if response_type == "system_info_update":
                        # Format system info data
                        formatted_data = self._format_powershell_system_info(json_data)
                        
                        # Send system info update
                        update_msg = {{
                            "type": "system_info_update",
                            "data": formatted_data,
                            "request_id": request_id,
                            "timestamp": datetime.now().isoformat()
                        }}
                        await self.websocket.send(json.dumps(update_msg))
                        logger.info("PowerShell system info update sent")
                    else:
                        # Send generic PowerShell result
                        response_msg = {{
                            "type": "powershell_result",
                            "request_id": request_id,
                            "data": json_data,
                            "success": True,
                            "timestamp": datetime.now().isoformat()
                        }}
                        await self.websocket.send(json.dumps(response_msg))
                        
                except json.JSONDecodeError:
                    # If not JSON, send as plain text result
                    response_msg = {{
                        "type": "powershell_result",
                        "request_id": request_id,
                        "data": {{"output": result['output']}},
                        "success": True,
                        "timestamp": datetime.now().isoformat()
                    }}
                    await self.websocket.send(json.dumps(response_msg))
            else:
                # Send error response
                response_msg = {{
                    "type": "powershell_result",
                    "request_id": request_id,
                    "data": {{"error": result.get('error', 'Command failed')}},
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }}
                await self.websocket.send(json.dumps(response_msg))
                
        except Exception as e:
            logger.error(f"Error executing PowerShell JSON command: {{e}}")
            # Send error response
            if self.websocket:
                error_response = {{
                    "type": "powershell_result",
                    "request_id": message_data.get("request_id"),
                    "data": {{"error": str(e)}},
                    "success": False,
                    "timestamp": datetime.now().isoformat()
                }}
                await self.websocket.send(json.dumps(error_response))
    
    def _format_powershell_system_info(self, ps_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format PowerShell system info data for compatibility"""
        try:
            # Format disk usage
            disk_usage = {{}}
            for drive, info in ps_data.get('disk_usage', {{}}).items():
                disk_usage[drive] = info.get('percent', 0)
            
            return {{
                "cpu_usage": round(ps_data.get('cpu_usage', 0), 1),
                "cpu_percent": round(ps_data.get('cpu_usage', 0), 1),
                "cpu_name": ps_data.get('cpu_name', 'Unknown'),
                "memory_usage": round(ps_data.get('memory', {{}}).get('usage', 0), 1),
                "memory_percent": round(ps_data.get('memory', {{}}).get('usage', 0), 1),
                "disk_usage": disk_usage,
                "disk_percent": disk_usage.get('C:', 0),
                "uptime": ps_data.get('uptime_seconds', 0),
                "hostname": ps_data.get('hostname', socket.gethostname()),
                "platform": ps_data.get('platform', platform.platform()),
                "architecture": "64bit" if ps_data.get('architecture', True) else "32bit",
                "cpu_count": ps_data.get('cpu_count', 0),
                "total_memory": ps_data.get('memory', {{}}).get('total', 0),
                "available_memory": ps_data.get('memory', {{}}).get('available', 0),
                "network_adapters": ps_data.get('network_adapters', []),
                "process_count": ps_data.get('processes', 0),
                "top_processes": ps_data.get('top_processes', []),
                "services": ps_data.get('services', {{}}),
                "raw_powershell_data": ps_data
            }}
        except Exception as e:
            logger.error(f"Error formatting PowerShell system info: {{e}}")
            return {{}}
    
    async def disconnect(self):
        """Disconnect from server"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
        logger.info("Agent disconnected")

async def main():
    """Main function"""
    agent = DexAgent()
    
    try:
        logger.info(f"Starting DexAgent {{agent.agent_name}}")
        logger.info(f"Connecting to server: {{agent.server_url}}")
        
        while True:
            try:
                await agent.connect()
            except KeyboardInterrupt:
                logger.info("Shutdown requested by user")
                break
            except Exception as e:
                logger.error(f"Agent error: {{e}}")
                logger.info("Retrying in 10 seconds...")
                await asyncio.sleep(10)
    
    except KeyboardInterrupt:
        logger.info("Agent stopped by user")
    finally:
        await agent.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
'''

    @staticmethod
    def _generate_requirements() -> str:
        """Generate requirements.txt content"""
        return """websockets>=11.0.0
psutil>=5.9.0
asyncio-mqtt>=0.11.1
"""

    @staticmethod
    def _generate_launcher_bat(agent_name: str) -> str:
        """Generate batch launcher script"""
        return f'''@echo off
title DexAgent - {agent_name}
echo Starting DexAgent - {agent_name}
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import websockets, psutil" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting agent...
echo Press Ctrl+C to stop the agent
echo.

python agent.py

pause
'''

    @staticmethod
    def _generate_install_bat() -> str:
        """Generate installation script"""
        return '''@echo off
title DexAgent Installation
echo DexAgent Installation Script
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or later from https://python.org
    echo.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found. Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo Installation completed successfully!
    echo.
    echo To start the agent, run: start_*.bat
    echo.
) else (
    echo.
    echo ERROR: Installation failed
    echo Please check your internet connection and try again
    echo.
)

pause
'''

    @staticmethod
    def _generate_readme(agent_name: str, server_url: str) -> str:
        """Generate README.md content"""
        return f'''# DexAgent - {agent_name}

Simple Python-based Windows agent for DexAgent management system.

## Quick Start

1. **Install Dependencies**
   ```
   Double-click: install.bat
   ```

2. **Start Agent**
   ```
   Double-click: start_{agent_name.lower()}.bat
   ```

## Requirements

- Python 3.8 or later
- Windows operating system
- Internet connection to reach server at: {server_url}

## Files

- `agent.py` - Main agent code
- `requirements.txt` - Python dependencies
- `install.bat` - Dependency installer
- `start_{agent_name.lower()}.bat` - Agent launcher
- `README.md` - This file

## Configuration

The agent is pre-configured to connect to:
- Server: {server_url}
- Agent Name: {agent_name}

## Features

- Automatic server connection with WebSocket
- PowerShell and CMD command execution
- Real-time system monitoring
- Automatic reconnection on connection loss
- Detailed logging to `agent.log`

## Troubleshooting

1. **Python not found**: Install Python from https://python.org
2. **Dependencies fail**: Run `install.bat` as administrator
3. **Connection issues**: Check server URL and network connectivity
4. **Logs**: Check `agent.log` for detailed error information

## Manual Installation

If batch files don't work:

```bash
# Install dependencies
pip install -r requirements.txt

# Start agent
python agent.py
```

## Support

For support, check the DexAgent management console or contact your system administrator.
'''

    @staticmethod
    def cleanup_temp_files(file_path: str):
        """Clean up temporary files"""
        try:
            if os.path.exists(file_path):
                # Remove the zip file
                os.remove(file_path)
                
                # Remove the temp directory
                temp_dir = os.path.dirname(file_path)
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
                logger.info(f"Cleaned up temporary files: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")