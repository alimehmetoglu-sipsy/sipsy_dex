import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from ...core.websocket_manager import websocket_manager
from ...core.database import db_manager
from ...schemas.agent import WebSocketMessage, AgentCommand, CommandResult
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/agent")
async def agent_websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for Python agent communication"""
    connection_id = None
    agent_id = None
    
    try:
        # Accept WebSocket connection first
        await websocket.accept()
        logger.info("New agent WebSocket connection accepted")
        
        # Wait for registration message
        data = await websocket.receive_text()
        message = json.loads(data)
        
        if message.get("type") != "register":
            await websocket.send_text(json.dumps({
                "type": "error",
                "data": {"message": "First message must be registration"}
            }))
            return
        
        # Extract agent info from registration
        agent_data = message.get("data", {})
        agent_id = agent_data.get("id")
        
        if not agent_id:
            await websocket.send_text(json.dumps({
                "type": "error", 
                "data": {"message": "Agent ID required in registration"}
            }))
            return
        
        # Register connection (don't accept again)
        connection_id = await websocket_manager.connect(websocket, agent_id, accept=False)
        
        # Update agent in database
        agent_data["status"] = "online"
        agent_data["last_seen"] = datetime.now().isoformat()
        db_manager.add_agent(agent_data)
        
        logger.info(f"Agent {agent_id} registered and connected via WebSocket")
        
        # Send welcome message
        welcome_message = {
            "type": "welcome",
            "data": {
                "agent_id": agent_id,
                "connection_id": connection_id,
                "message": "Connected to DexAgents server"
            },
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_message))
        
        # Listen for messages from agent
        while True:
            try:
                # Receive message from agent
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Update heartbeat
                websocket_manager.update_heartbeat(connection_id)
                
                # Handle different message types
                await handle_agent_message(agent_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"Agent {agent_id} disconnected")
                break
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from agent {agent_id}")
                continue
            except Exception as e:
                logger.error(f"Error handling message from agent {agent_id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"WebSocket error for agent {agent_id}: {str(e)}")
    finally:
        # Clean up connection
        if connection_id and agent_id:
            websocket_manager.disconnect(connection_id)
            db_manager.update_agent_status(agent_id, "offline")
            logger.info(f"Agent {agent_id} connection cleaned up")

@router.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for agent communication"""
    connection_id = None
    
    try:
        # Accept the WebSocket connection
        connection_id = await websocket_manager.connect(websocket, agent_id)
        
        # Update agent connection status
        db_manager.update_agent_connection(agent_id, connection_id, True)
        
        logger.info(f"Agent {agent_id} connected via WebSocket")
        
        # Send welcome message
        welcome_message = {
            "type": "welcome",
            "data": {
                "agent_id": agent_id,
                "connection_id": connection_id,
                "message": "Connected to DexAgents server"
            },
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_message))
        
        # Listen for messages from agent
        while True:
            try:
                # Receive message from agent
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Update heartbeat
                websocket_manager.update_heartbeat(connection_id)
                
                # Handle different message types
                await handle_agent_message(agent_id, message)
                
            except WebSocketDisconnect:
                logger.info(f"Agent {agent_id} disconnected")
                break
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON from agent {agent_id}")
                continue
            except Exception as e:
                logger.error(f"Error handling message from agent {agent_id}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"WebSocket error for agent {agent_id}: {str(e)}")
    finally:
        # Clean up connection
        if connection_id:
            websocket_manager.disconnect(connection_id)
            db_manager.update_agent_connection(agent_id, None, False)
            logger.info(f"Agent {agent_id} connection cleaned up")

async def handle_agent_message(agent_id: str, message: Dict[str, Any]):
    """Handle messages from agent"""
    try:
        # Debug log the raw message
        logger.info(f"Raw message from agent {agent_id}: {type(message)} - {message}")
        
        # If message is string, try to parse as JSON
        if isinstance(message, str):
            try:
                message = json.loads(message)
                logger.info(f"Parsed JSON message: {message}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON message from agent {agent_id}: {e}")
                return
        
        message_type = message.get("type")
    except Exception as e:
        logger.error(f"Error handling message from agent {agent_id}: {e}")
        logger.error(f"Message type: {type(message)}, content: {message}")
        return
    
    if message_type == "heartbeat":
        # Update agent status with system info
        system_info = message.get("data", {}).get("system_info", {})
        db_manager.update_agent_status(agent_id, "online", system_info)
        
    elif message_type == "command_result":
        # Handle command execution result
        command_result = message.get("data", {})
        command_id = command_result.get("command_id", "") or message.get("command_id", "")
        
        logger.info(f"Command result received from agent {agent_id}, command_id: {command_id}")
        logger.info(f"Command result data: {command_result}")
        
        # Store command response in WebSocket manager
        if command_id:
            # Extract result data - support new Python agent format
            response_data = {
                "success": command_result.get("success", False),
                "output": command_result.get("output", ""),
                "error": command_result.get("error", ""),
                "return_code": command_result.get("return_code", 0),
                "execution_time": command_result.get("execution_time", 0.0),
                "timestamp": command_result.get("timestamp", datetime.now().isoformat())
            }
            websocket_manager.store_command_response(command_id, response_data)
            logger.info(f"Command response stored for command_id: {command_id}")
        else:
            logger.warning(f"No command_id in command result from agent {agent_id}")
            
    elif message_type == "powershell_result":
        # Handle PowerShell command result
        request_id = message.get("request_id")
        data = message.get("data", {})
        success = message.get("success", False)
        
        logger.info(f"PowerShell result received from agent {agent_id}, request_id: {request_id}")
        logger.info(f"PowerShell result data: {data}")
        
        if request_id:
            # Format response data for PowerShell results
            # Handle both dict and list data types
            error_msg = ""
            execution_time = 0.0
            
            if isinstance(data, dict):
                error_msg = data.get("error", "") if not success else ""
                execution_time = data.get("execution_time", 0.0)
            
            response_data = {
                "status": "completed",
                "success": success,
                "output": data,
                "error": error_msg,
                "execution_time": execution_time,
                "timestamp": message.get("timestamp", datetime.now().isoformat())
            }
            websocket_manager.store_command_response(request_id, response_data)
            logger.info(f"PowerShell response stored for request_id: {request_id}")
        else:
            logger.warning(f"No request_id in PowerShell result from agent {agent_id}")
        
        # Also store in database (ignore database errors for now)
        try:
            db_manager.add_command_history(agent_id, {
                "command": data.get("command", "") if isinstance(data, dict) else "",
                "success": success,
                "output": data,
                "error": error_msg,
                "execution_time": execution_time
            })
        except Exception as e:
            logger.warning(f"Could not store command history in database: {e}")
        
        logger.info(f"PowerShell result processed for agent {agent_id}: {success}")
    
    elif message_type == "system_info_update":
        # Handle system info update from agent
        system_info = message.get("data", {})
        logger.info(f"System info update received from agent {agent_id}: {system_info}")
        
        # Update agent in database with new system info
        try:
            update_data = {
                "system_info": system_info,
                "last_seen": datetime.now().isoformat()
            }
            db_manager.update_agent(agent_id, update_data)
            logger.info(f"Agent {agent_id} system info updated in database")
        except Exception as e:
            logger.error(f"Error updating agent {agent_id} system info: {str(e)}")
    
    elif message_type == "pong":
        # Handle pong response
        logger.debug(f"Pong received from agent {agent_id}")
        
    elif message_type == "register":
        # Handle agent registration - this is redundant for new endpoint but keep for compatibility  
        logger.info(f"Received redundant registration from agent {agent_id}")
        
    else:
        logger.warning(f"Unknown message type from agent {agent_id}: {message_type}")

@router.post("/send/{agent_id}/command")
async def send_command_to_agent(agent_id: str, command: AgentCommand):
    """Send command to specific agent via WebSocket"""
    if not websocket_manager.is_agent_connected(agent_id):
        raise HTTPException(status_code=404, detail="Agent not connected")
    
    # Generate command ID for tracking
    import uuid
    command_id = str(uuid.uuid4())
    
    message = {
        "type": "command",
        "data": {
            "id": command_id,
            "type": getattr(command, 'command_type', 'powershell'),
            "command": command.command,
            "timeout": command.timeout,
            "working_directory": command.working_directory
        },
        "timestamp": datetime.now().isoformat()
    }
    
    success = await websocket_manager.send_to_agent(agent_id, message)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send command to agent")
    
    return {"message": "Command sent to agent", "agent_id": agent_id, "command_id": command_id}

@router.get("/connected")  
async def get_connected_agents():
    """Get list of connected agents"""
    try:
        connected_agents = websocket_manager.get_connected_agents()
        agents_info = []
        
        for agent_id in connected_agents:
            agent_data = db_manager.get_agent(agent_id)
            if agent_data:
                try:
                    connection_info = websocket_manager.get_connection_info(
                        websocket_manager.agent_connections[agent_id]
                    )
                    agent_data["connection_info"] = connection_info
                except Exception as e:
                    logger.warning(f"Could not get connection info for agent {agent_id}: {e}")
                agents_info.append(agent_data)
        
        return {"connected_agents": agents_info, "count": len(agents_info)}
    except Exception as e:
        logger.error(f"Error getting connected agents: {e}")
        return {"connected_agents": [], "count": 0, "error": str(e)} 