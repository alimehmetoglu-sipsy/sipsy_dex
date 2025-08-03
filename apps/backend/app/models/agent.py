from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

class AgentStatus(Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class Agent:
    """Agent model representing a connected agent"""
    id: str
    hostname: str
    ip: Optional[str] = None
    os: Optional[str] = None
    version: Optional[str] = None
    status: AgentStatus = AgentStatus.OFFLINE
    last_seen: Optional[datetime] = None
    tags: List[str] = None
    system_info: Dict[str, Any] = None
    connection_id: Optional[str] = None
    is_connected: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.system_info is None:
            self.system_info = {}
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.last_seen is None:
            self.last_seen = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            'id': self.id,
            'hostname': self.hostname,
            'ip': self.ip,
            'os': self.os,
            'version': self.version,
            'status': self.status.value if isinstance(self.status, AgentStatus) else self.status,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'tags': self.tags,
            'system_info': self.system_info,
            'connection_id': self.connection_id,
            'is_connected': self.is_connected,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create agent from dictionary"""
        # Convert status string to enum
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = AgentStatus(data['status'])
        
        # Convert datetime strings to datetime objects
        for field in ['last_seen', 'created_at', 'updated_at']:
            if field in data and data[field] and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        
        return cls(**data)