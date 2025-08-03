from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class Agent(BaseModel):
    id: Optional[str] = None
    hostname: str
    ip: Optional[str] = None
    os: Optional[str] = None
    version: Optional[str] = None
    status: str = "offline"
    last_seen: Optional[str] = None
    tags: List[str] = []
    system_info: Optional[Dict[str, Any]] = None
    connection_id: Optional[str] = None
    is_connected: bool = False

class AgentUpdate(BaseModel):
    hostname: Optional[str] = None
    ip: Optional[str] = None
    os: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    system_info: Optional[Dict[str, Any]] = None
    connection_id: Optional[str] = None
    is_connected: Optional[bool] = None

class AgentRegister(BaseModel):
    hostname: str
    ip: Optional[str] = None
    os: Optional[str] = None
    version: Optional[str] = None
    tags: List[str] = []
    system_info: Optional[Dict[str, Any]] = None

class AgentInstallerConfig(BaseModel):
    server_url: str = Field(..., description="DexAgents server URL")
    api_token: str = Field(..., description="API token for authentication")
    agent_name: Optional[str] = Field(None, description="Custom agent name")
    tags: List[str] = Field(default_factory=list, description="Agent tags")
    auto_start: bool = Field(True, description="Auto-start agent after installation")
    run_as_service: bool = Field(True, description="Run agent as Windows service")

class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: Optional[str] = None

class AgentCommand(BaseModel):
    command: str
    timeout: Optional[int] = 30
    working_directory: Optional[str] = None

class CommandResult(BaseModel):
    command: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    exit_code: Optional[int] = None 