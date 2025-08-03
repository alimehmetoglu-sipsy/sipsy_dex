from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class AgentGroup:
    """Agent group model for organizing agents"""
    id: Optional[int] = None
    name: str = None
    description: Optional[str] = None
    agent_ids: List[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.agent_ids is None:
            self.agent_ids = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert group to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'agent_ids': self.agent_ids,
            'agent_count': len(self.agent_ids),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentGroup':
        """Create group from dictionary"""
        # Convert datetime strings to datetime objects
        for field in ['created_at', 'updated_at']:
            if field in data and data[field] and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        
        # Remove derived fields
        data.pop('agent_count', None)
        
        return cls(**data)