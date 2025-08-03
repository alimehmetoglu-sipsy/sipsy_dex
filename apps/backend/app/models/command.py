from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class CommandHistory:
    """Command execution history model"""
    id: Optional[int] = None
    agent_id: str = None
    command: str = None
    success: bool = False
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert command history to dictionary"""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'command': self.command,
            'success': self.success,
            'output': self.output,
            'error': self.error,
            'execution_time': self.execution_time,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandHistory':
        """Create command history from dictionary"""
        # Convert timestamp string to datetime object
        if 'timestamp' in data and data['timestamp'] and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        
        return cls(**data)