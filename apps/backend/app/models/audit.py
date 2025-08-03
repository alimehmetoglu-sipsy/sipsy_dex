from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class AuditLog:
    """Audit log model for tracking user actions"""
    id: Optional[int] = None
    user_id: Optional[int] = None
    action: str = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert audit log to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditLog':
        """Create audit log from dictionary"""
        # Convert timestamp string to datetime object
        if 'timestamp' in data and data['timestamp'] and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        
        return cls(**data)
    
    def get_description(self) -> str:
        """Get a human-readable description of the action"""
        descriptions = {
            'login': f"User logged in",
            'logout': f"User logged out",
            'create': f"Created {self.resource_type} {self.resource_id}",
            'update': f"Updated {self.resource_type} {self.resource_id}",
            'delete': f"Deleted {self.resource_type} {self.resource_id}",
            'execute': f"Executed command on {self.resource_type} {self.resource_id}",
            'connect': f"Connected to {self.resource_type} {self.resource_id}",
            'disconnect': f"Disconnected from {self.resource_type} {self.resource_id}"
        }
        
        return descriptions.get(self.action, f"{self.action} on {self.resource_type} {self.resource_id}")