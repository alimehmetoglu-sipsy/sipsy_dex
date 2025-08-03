import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.agent_connections: Dict[str, str] = {}  # agent_id -> connection_id
        self.connection_agents: Dict[str, str] = {}  # connection_id -> agent_id
        self.connection_info: Dict[str, Dict[str, Any]] = {}
        self.pending_commands: Dict[str, Dict[str, Any]] = {}  # command_id -> command_info
        self.command_responses: Dict[str, Dict[str, Any]] = {}  # command_id -> response
        self.response_events: Dict[str, asyncio.Event] = {}  # command_id -> event for waiting responses
    
    async def connect(self, websocket: WebSocket, agent_id: Optional[str] = None, accept: bool = True) -> str:
        """Accept WebSocket connection and return connection ID"""
        if accept:
            await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        
        if agent_id:
            self.agent_connections[agent_id] = connection_id
            self.connection_agents[connection_id] = agent_id
            logger.info(f"Agent {agent_id} mapped to connection {connection_id}")
            logger.info(f"Current agent connections: {list(self.agent_connections.keys())}")
        
        self.connection_info[connection_id] = {
            "connected_at": datetime.now().isoformat(),
            "agent_id": agent_id,
            "last_heartbeat": datetime.now().isoformat()
        }
        
        logger.info(f"WebSocket connected: {connection_id} (Agent: {agent_id})")
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Remove WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if connection_id in self.connection_agents:
            agent_id = self.connection_agents[connection_id]
            if agent_id in self.agent_connections:
                del self.agent_connections[agent_id]
            del self.connection_agents[connection_id]
        
        if connection_id in self.connection_info:
            del self.connection_info[connection_id]
        
        logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def send_message(self, connection_id: str, message: Dict[str, Any]):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {str(e)}")
                self.disconnect(connection_id)
                return False
        return False
    
    async def send_to_agent(self, agent_id: str, message: Dict[str, Any]):
        """Send message to specific agent"""
        if agent_id in self.agent_connections:
            connection_id = self.agent_connections[agent_id]
            return await self.send_message(connection_id, message)
        return False
    
    async def execute_command_on_agent(self, agent_id: str, command: Dict[str, Any]) -> str:
        """Execute PowerShell command on agent and return command ID"""
        logger.info(f"Attempting to execute PowerShell command on agent {agent_id}")
        logger.info(f"Connected agents: {list(self.agent_connections.keys())}")
        
        if agent_id not in self.agent_connections:
            logger.error(f"Agent {agent_id} is not connected. Available agents: {list(self.agent_connections.keys())}")
            raise ValueError(f"Agent {agent_id} is not connected")
        
        # Use PowerShell-specific request ID format to match agent expectations
        request_id = f"ps_{datetime.now().timestamp()}_{uuid.uuid4().hex[:8]}"
        
        # Store command info
        self.pending_commands[request_id] = {
            "agent_id": agent_id,
            "command": command.get("command", ""),
            "timestamp": datetime.now(),
            "status": "pending"
        }
        
        # Send PowerShell command to agent in the format it expects
        powershell_message = {
            "type": "powershell_command",
            "request_id": request_id,
            "command": command.get("command", ""),
            "timeout": command.get("timeout", 30),
            "working_directory": command.get("working_directory"),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Sending PowerShell command {request_id} to agent {agent_id}: {powershell_message}")
        success = await self.send_to_agent(agent_id, powershell_message)
        if not success:
            del self.pending_commands[request_id]
            logger.error(f"Failed to send PowerShell command to agent {agent_id}")
            raise ValueError(f"Failed to send PowerShell command to agent {agent_id}")
        
        logger.info(f"PowerShell command {request_id} sent to agent {agent_id}")
        return request_id
    
    def store_command_response(self, command_id: str, response: Dict[str, Any]):
        """Store command response from agent"""
        self.command_responses[command_id] = response
        if command_id in self.pending_commands:
            self.pending_commands[command_id]["status"] = "completed"
            self.pending_commands[command_id]["response"] = response
        
        # Signal waiting threads that response is ready
        if command_id in self.response_events:
            self.response_events[command_id].set()
        
        logger.info(f"Command response stored for {command_id}")
    
    def get_command_response(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get command response"""
        response = self.command_responses.get(command_id)
        if response:
            logger.info(f"Found command response for {command_id}: {response.get('success', False)}")
        else:
            logger.debug(f"No command response found for {command_id}")
        return response
    
    def get_pending_command(self, command_id: str) -> Optional[Dict[str, Any]]:
        """Get pending command info"""
        return self.pending_commands.get(command_id)
    
    async def wait_for_command_response(self, command_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
        """Wait for command response with timeout"""
        try:
            # Check if response already exists
            if command_id in self.command_responses:
                return self.command_responses[command_id]
            
            # Create event if not exists
            if command_id not in self.response_events:
                self.response_events[command_id] = asyncio.Event()
            
            # Wait for response with timeout
            await asyncio.wait_for(self.response_events[command_id].wait(), timeout=timeout)
            
            # Cleanup event
            if command_id in self.response_events:
                del self.response_events[command_id]
            
            return self.command_responses.get(command_id)
        
        except asyncio.TimeoutError:
            logger.warning(f"Command {command_id} timed out after {timeout} seconds")
            # Cleanup
            if command_id in self.response_events:
                del self.response_events[command_id]
            if command_id in self.pending_commands:
                self.pending_commands[command_id]["status"] = "timeout"
            return None
        except Exception as e:
            logger.error(f"Error waiting for command response {command_id}: {str(e)}")
            # Cleanup
            if command_id in self.response_events:
                del self.response_events[command_id]
            return None
    
    async def broadcast(self, message: Dict[str, Any], exclude_connection: Optional[str] = None):
        """Broadcast message to all connections"""
        disconnected = []
        
        for connection_id, websocket in self.active_connections.items():
            if connection_id != exclude_connection:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_id}: {str(e)}")
                    disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id)
    
    def get_connected_agents(self) -> Set[str]:
        """Get set of connected agent IDs"""
        return set(self.agent_connections.keys())
    
    def is_agent_connected(self, agent_id: str) -> bool:
        """Check if agent is connected"""
        return agent_id in self.agent_connections
    
    def get_connection_info(self, connection_id: str) -> Optional[Dict[str, Any]]:
        """Get connection information"""
        return self.connection_info.get(connection_id)
    
    def update_heartbeat(self, connection_id: str):
        """Update last heartbeat time"""
        if connection_id in self.connection_info:
            self.connection_info[connection_id]["last_heartbeat"] = datetime.now().isoformat()
    
    async def request_system_info(self, agent_id: str) -> str:
        """Request system information update from agent"""
        logger.info(f"Requesting system info from agent {agent_id}")
        
        if agent_id not in self.agent_connections:
            logger.error(f"Agent {agent_id} is not connected")
            raise ValueError(f"Agent {agent_id} is not connected")
        
        request_id = f"sysinfo_{datetime.now().timestamp()}_{uuid.uuid4().hex[:8]}"
        
# PowerShell script to get complete system information
        powershell_script = """
$systemInfo = @{
    hostname = $env:COMPUTERNAME
    platform = [System.Environment]::OSVersion.VersionString
    architecture = [System.Environment]::Is64BitOperatingSystem
    cpu_count = (Get-CimInstance Win32_Processor).NumberOfLogicalProcessors
    cpu_name = (Get-CimInstance Win32_Processor).Name
    cpu_usage = (Get-Counter '\\\\Processor(_Total)\\\\% Processor Time' -SampleInterval 1).CounterSamples[0].CookedValue
    memory = @{
        total = (Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory
        available = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory * 1024
        usage = 100 - ((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / ((Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory / 1024)) * 100
    }
    disk_usage = @{}
    uptime_seconds = (New-TimeSpan -Start (Get-CimInstance Win32_OperatingSystem).LastBootUpTime -End (Get-Date)).TotalSeconds
    network_adapters = @()
    processes = (Get-Process).Count
    top_processes = @()
    services = @{
        total = (Get-Service).Count
        running = (Get-Service | Where-Object {$_.Status -eq 'Running'}).Count
        stopped = (Get-Service | Where-Object {$_.Status -eq 'Stopped'}).Count
    }
}

# Get disk usage for all drives
Get-WmiObject Win32_LogicalDisk -Filter "DriveType=3" | ForEach-Object {
    $systemInfo.disk_usage[$_.DeviceID] = @{
        total = $_.Size
        free = $_.FreeSpace
        used = $_.Size - $_.FreeSpace
        percent = [math]::Round((($_.Size - $_.FreeSpace) / $_.Size) * 100, 1)
    }
}

# Get network adapter info
Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object {
    $ipConfig = Get-NetIPAddress -InterfaceIndex $_.InterfaceIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue
    $adapter = @{
        name = $_.Name
        description = $_.InterfaceDescription
        mac = $_.MacAddress
        speed = $_.LinkSpeed
        ip = if($ipConfig) { $ipConfig.IPAddress } else { "N/A" }
    }
    $systemInfo.network_adapters += $adapter
}

# Get top 5 processes by CPU
Get-Process | Sort-Object CPU -Descending | Select-Object -First 5 | ForEach-Object {
    $process = @{
        name = $_.ProcessName
        id = $_.Id
        cpu = [math]::Round($_.CPU, 2)
        memory_mb = [math]::Round($_.WorkingSet / 1MB, 2)
    }
    $systemInfo.top_processes += $process
}

# Convert to JSON
$systemInfo | ConvertTo-Json -Depth 10 -Compress
"""
        
        # Send PowerShell command request to agent
        request_message = {
            "type": "powershell_command",
            "request_id": request_id,
            "command": powershell_script,
            "response_type": "system_info_update",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Sending PowerShell system info request {request_id} to agent {agent_id}")
        success = await self.send_to_agent(agent_id, request_message)
        
        if not success:
            logger.error(f"Failed to send system info request to agent {agent_id}")
            raise ValueError(f"Failed to send system info request to agent {agent_id}")
        
        return request_id

# Global WebSocket manager instance
websocket_manager = WebSocketManager() 