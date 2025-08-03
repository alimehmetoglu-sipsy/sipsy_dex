from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from ...schemas.agent import Agent, AgentUpdate, AgentRegister
from ...core.database import db_manager
from ...core.auth import verify_token
from ...core.websocket_manager import websocket_manager
import logging
import socket
import platform
import psutil
from datetime import datetime
import json
import asyncio
from ...schemas.command import PowerShellCommand, CommandResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[Agent])
async def get_agents(token: str = Depends(verify_token)):
    """Get all agents"""
    try:
        agents_data = db_manager.get_agents()
        agents = []
        
        for agent_data in agents_data:
            # Check if agent is currently connected
            agent_data['is_connected'] = websocket_manager.is_agent_connected(agent_data['id'])
            agents.append(Agent(**agent_data))
        
        return agents
    except Exception as e:
        logger.error(f"Error getting agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, token: str = Depends(verify_token)):
    """Get a specific agent by ID"""
    try:
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is currently connected
        agent_data['is_connected'] = websocket_manager.is_agent_connected(agent_id)
        return Agent(**agent_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/register", response_model=Agent)
async def register_agent(agent_data: AgentRegister, token: str = Depends(verify_token)):
    """Register a new agent"""
    try:
        # Check if agent with same hostname already exists
        existing_agent = db_manager.get_agent_by_hostname(agent_data.hostname)
        if existing_agent:
            # Update existing agent instead of creating new one
            update_data = agent_data.dict(exclude_unset=True)
            update_data['status'] = 'online'
            update_data['last_seen'] = datetime.now().isoformat()
            
            db_manager.update_agent(existing_agent['id'], update_data)
            existing_agent.update(update_data)
            existing_agent['is_connected'] = websocket_manager.is_agent_connected(existing_agent['id'])
            
            logger.info(f"Agent {existing_agent['id']} updated during registration")
            return Agent(**existing_agent)
        
        # Create new agent
        agent_dict = agent_data.dict()
        agent_dict['status'] = 'online'
        agent_dict['last_seen'] = datetime.now().isoformat()
        
        agent_id = db_manager.add_agent(agent_dict)
        agent_dict['id'] = agent_id
        agent_dict['is_connected'] = False  # Will be updated when WebSocket connects
        
        logger.info(f"New agent {agent_id} registered")
        return Agent(**agent_dict)
        
    except Exception as e:
        logger.error(f"Error registering agent: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, agent_update: AgentUpdate, token: str = Depends(verify_token)):
    """Update an existing agent"""
    try:
        # Get current agent data
        current_agent = db_manager.get_agent(agent_id)
        if not current_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update only provided fields
        update_data = agent_update.dict(exclude_unset=True)
        success = db_manager.update_agent(agent_id, update_data)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update agent")
        
        # Return updated agent
        updated_agent = db_manager.get_agent(agent_id)
        updated_agent['is_connected'] = websocket_manager.is_agent_connected(agent_id)
        return Agent(**updated_agent)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, token: str = Depends(verify_token)):
    """Delete an agent"""
    try:
        success = db_manager.delete_agent(agent_id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"message": "Agent deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{agent_id}/command", response_model=CommandResponse)
async def execute_agent_command(
    agent_id: str,
    command: PowerShellCommand,
    token: str = Depends(verify_token)
):
    """Execute a PowerShell command on a specific agent"""
    try:
        # Check if agent exists and is online
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected via WebSocket
        if agent_id not in websocket_manager.agent_connections:
            raise HTTPException(status_code=400, detail="Agent is not connected")
        
        # Execute command on agent via WebSocket
        command_data = {
            "command": command.command,
            "timeout": command.timeout or 30,
            "working_directory": command.working_directory,
            "run_as_admin": command.run_as_admin or False
        }
        
        # Send command to agent and get command ID
        command_id = await websocket_manager.execute_command_on_agent(agent_id, command_data)
        
        # Wait for response (with timeout)
        timeout_seconds = command.timeout or 30
        start_time = datetime.now()
        
        logger.info(f"Waiting for command response: {command_id}, timeout: {timeout_seconds}s")
        
        while (datetime.now() - start_time).total_seconds() < timeout_seconds:
            response = websocket_manager.get_command_response(command_id)
            if response:
                logger.info(f"Command response received for {command_id}: {response.get('success', False)}")
                # Convert agent response to CommandResponse
                return CommandResponse(
                    success=response.get("success", False),
                    output=response.get("output", ""),
                    error=response.get("error"),
                    execution_time=response.get("execution_time", 0.0),
                    timestamp=response.get("timestamp", datetime.now().isoformat()),
                    command=command.command
                )
            
            await asyncio.sleep(0.1)  # Wait 100ms before checking again
        
        # Timeout reached
        logger.warning(f"Command {command_id} timed out for agent {agent_id}")
        return CommandResponse(
            success=False,
            output="",
            error=f"Command timed out after {timeout_seconds} seconds",
            execution_time=timeout_seconds,
            timestamp=datetime.now().isoformat(),
            command=command.command
        )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing command on agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to execute command on agent")

@router.get("/{agent_id}/commands", response_model=List[CommandResponse])
async def get_agent_command_history(
    agent_id: str,
    limit: int = 50,
    token: str = Depends(verify_token)
):
    """Get command execution history for a specific agent"""
    try:
        # Check if agent exists
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get command history from database
        commands = db_manager.get_agent_commands(agent_id, limit)
        return commands
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting command history for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get command history")

@router.post("/{agent_id}/refresh")
async def refresh_agent(agent_id: str, token: str = Depends(verify_token)):
    """Refresh agent status and return updated agent data"""
    try:
        logger.info(f"Refresh request received for agent {agent_id}")
        
        # Verify agent exists
        agent = db_manager.get_agent(agent_id)
        if not agent:
            logger.error(f"Agent {agent_id} not found")
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is currently connected via WebSocket
        is_connected = websocket_manager.is_agent_connected(agent_id)
        logger.info(f"Agent {agent_id} connection status: {is_connected}")
        
        # If agent is connected, request system info via WebSocket
        if is_connected:
            try:
                # Request system info from agent
                request_id = await websocket_manager.request_system_info(agent_id)
                logger.info(f"System info request {request_id} sent to agent {agent_id}")
                
                # Wait briefly for agent to respond (we'll handle the actual update via WebSocket)
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error requesting system info from agent {agent_id}: {str(e)}")
        
        # Update agent status based on connection
        status = 'online' if is_connected else 'offline'
        update_data = {
            'status': status,
            'last_seen': datetime.now().isoformat()
        }
        
        logger.info(f"Updating agent {agent_id} with data: {update_data}")
        success = db_manager.update_agent(agent_id, update_data)
        
        if not success:
            logger.error(f"Failed to update agent {agent_id}")
            raise HTTPException(status_code=500, detail="Failed to refresh agent")
        
        # Get updated agent data
        updated_agent = db_manager.get_agent(agent_id)
        updated_agent['is_connected'] = is_connected
        
        logger.info(f"Agent {agent_id} updated successfully")
        logger.info(f"Returning agent data: {updated_agent}")
        
        return {
            "message": "Agent refreshed successfully",
            "agent": Agent(**updated_agent)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/connected", response_model=List[Agent])
async def get_connected_agents(token: str = Depends(verify_token)):
    """Get list of currently connected agents"""
    try:
        connected_agents = websocket_manager.get_connected_agents()
        agents_info = []
        
        for agent_id in connected_agents:
            agent_data = db_manager.get_agent(agent_id)
            if agent_data:
                agent_data['is_connected'] = True
                connection_info = websocket_manager.get_connection_info(
                    websocket_manager.agent_connections[agent_id]
                )
                agent_data['connection_info'] = connection_info
                agents_info.append(Agent(**agent_data))
        
        return agents_info
    except Exception as e:
        logger.error(f"Error getting connected agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/offline", response_model=List[Agent])
async def get_offline_agents(token: str = Depends(verify_token)):
    """Get list of agents that haven't sent heartbeat in the last 60 seconds"""
    try:
        from datetime import timedelta
        
        # Get all agents
        all_agents = db_manager.get_agents()
        offline_agents = []
        
        # Check which agents haven't sent heartbeat recently
        cutoff_time = datetime.now() - timedelta(seconds=60)
        
        for agent_data in all_agents:
            last_seen_str = agent_data.get('last_seen')
            if last_seen_str:
                try:
                    last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                    if last_seen < cutoff_time:
                        agent_data['is_connected'] = False
                        offline_agents.append(Agent(**agent_data))
                except ValueError:
                    # If last_seen is invalid, consider agent offline
                    agent_data['is_connected'] = False
                    offline_agents.append(Agent(**agent_data))
            else:
                # No last_seen, consider offline
                agent_data['is_connected'] = False
                offline_agents.append(Agent(**agent_data))
        
        return offline_agents
    except Exception as e:
        logger.error(f"Error getting offline agents: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/status/{agent_id}")
async def get_agent_status(agent_id: str, token: str = Depends(verify_token)):
    """Get detailed status of an agent including heartbeat timing"""
    try:
        agent_data = db_manager.get_agent(agent_id)
        if not agent_data:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check if agent is connected via WebSocket
        is_websocket_connected = websocket_manager.is_agent_connected(agent_id)
        
        # Check heartbeat timing
        last_seen_str = agent_data.get('last_seen')
        heartbeat_status = "unknown"
        seconds_since_heartbeat = None
        
        if last_seen_str:
            try:
                last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                seconds_since_heartbeat = (datetime.now() - last_seen).total_seconds()
                
                if seconds_since_heartbeat < 30:
                    heartbeat_status = "recent"
                elif seconds_since_heartbeat < 60:
                    heartbeat_status = "stale"
                else:
                    heartbeat_status = "offline"
            except ValueError:
                heartbeat_status = "invalid_timestamp"
        
        # Determine overall status
        if is_websocket_connected:
            overall_status = "online"
        elif heartbeat_status == "recent":
            overall_status = "online"
        elif heartbeat_status == "stale":
            overall_status = "warning"
        else:
            overall_status = "offline"
        
        status_info = {
            "agent_id": agent_id,
            "overall_status": overall_status,
            "websocket_connected": is_websocket_connected,
            "heartbeat_status": heartbeat_status,
            "seconds_since_heartbeat": seconds_since_heartbeat,
            "last_seen": last_seen_str,
            "agent_data": Agent(**agent_data)
        }
        
        return status_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/seed", response_model=List[Agent])
async def seed_test_data(token: str = Depends(verify_token)):
    """Seed test data for development"""
    try:
        test_agents = [
            {
                "hostname": "DESKTOP-ABC123",
                "ip": "192.168.1.100",
                "os": "Windows 11",
                "version": "10.0.22000",
                "status": "online",
                "tags": ["development", "test"]
            },
            {
                "hostname": "LAPTOP-XYZ789",
                "ip": "192.168.1.101",
                "os": "Windows 10",
                "version": "10.0.19045",
                "status": "offline",
                "tags": ["production", "critical"]
            },
            {
                "hostname": "SERVER-MAIN",
                "ip": "192.168.1.102",
                "os": "Windows Server 2022",
                "version": "10.0.20348",
                "status": "online",
                "tags": ["server", "production", "database"]
            }
        ]
        
        created_agents = []
        for agent_data in test_agents:
            agent_id = db_manager.add_agent(agent_data)
            agent_data["id"] = agent_id
            agent_data["is_connected"] = websocket_manager.is_agent_connected(agent_id)
            created_agents.append(Agent(**agent_data))
        
        return created_agents
    except Exception as e:
        logger.error(f"Error seeding test data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{agent_id}/heartbeat")
async def agent_heartbeat(agent_id: str, token: str = Depends(verify_token)):
    """Agent heartbeat endpoint - called every 30 seconds to indicate agent is online"""
    try:
        logger.info(f"Heartbeat received from agent {agent_id}")
        
        # Verify agent exists
        agent = db_manager.get_agent(agent_id)
        if not agent:
            logger.error(f"Agent {agent_id} not found for heartbeat")
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get system information
        system_info = {}
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
            
            system_info = {
                "hostname": platform.node(),
                "os_version": platform.platform(),
                "cpu_usage": cpu_usage,
                "memory_usage": memory.percent,
                "disk_usage": disk_usage
            }
            
            logger.info(f"Retrieved system info for agent {agent_id}: {system_info}")
        except Exception as e:
            logger.error(f"Error getting system info for agent {agent_id}: {str(e)}")
            system_info = {}
        
        # Update agent status
        update_data = {
            'status': 'online',
            'last_seen': datetime.now().isoformat()
        }
        
        # Add system info if available
        if system_info:
            update_data['system_info'] = system_info
        
        logger.info(f"Updating agent {agent_id} heartbeat with data: {update_data}")
        success = db_manager.update_agent(agent_id, update_data)
        
        if not success:
            logger.error(f"Failed to update agent {agent_id} heartbeat")
            raise HTTPException(status_code=500, detail="Failed to update agent heartbeat")
        
        # Get updated agent data
        updated_agent = db_manager.get_agent(agent_id)
        updated_agent['is_connected'] = websocket_manager.is_agent_connected(agent_id)
        
        logger.info(f"Agent {agent_id} heartbeat updated successfully")
        
        return {
            "message": "Heartbeat received",
            "agent": Agent(**updated_agent),
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing heartbeat for agent {agent_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error") 