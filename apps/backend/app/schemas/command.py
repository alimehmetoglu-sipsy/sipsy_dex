from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class PowerShellCommand(BaseModel):
    command: str = Field(..., description="PowerShell command to execute")
    timeout: Optional[int] = Field(30, description="Command timeout in seconds")
    working_directory: Optional[str] = Field(None, description="Working directory for command")
    run_as_admin: Optional[bool] = Field(False, description="Run command as administrator")

class CommandResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float
    timestamp: datetime
    command: str

class CommandParameter(BaseModel):
    name: str = Field(..., description="Parameter name")
    type: str = Field("string", description="Parameter type (string, number, boolean)")
    default: Optional[str] = Field(None, description="Default value")
    description: Optional[str] = Field(None, description="Parameter description")
    required: bool = Field(False, description="Whether parameter is required")

class SavedPowerShellCommand(BaseModel):
    id: Optional[str] = Field(None, description="Command ID (auto-generated)")
    name: str = Field(..., description="Command display name")
    description: Optional[str] = Field(None, description="Command description")
    category: str = Field("general", description="Command category")
    command: str = Field(..., description="PowerShell command template")
    parameters: List[CommandParameter] = Field(default_factory=list, description="Command parameters")
    tags: List[str] = Field(default_factory=list, description="Command tags")
    version: str = Field("1.0", description="Command version")
    author: str = Field("Unknown", description="Command author")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    is_system: bool = Field(False, description="Whether this is a system command")

class PowerShellCommandExecution(BaseModel):
    command_id: str = Field(..., description="Saved command ID")
    parameters: dict = Field(default_factory=dict, description="Parameter values")
    agent_ids: List[str] = Field(..., description="Target agent IDs")
    timeout: Optional[int] = Field(30, description="Execution timeout")

class BatchCommandExecution(BaseModel):
    commands: List[PowerShellCommandExecution] = Field(..., description="Commands to execute")
    parallel: bool = Field(False, description="Execute commands in parallel") 