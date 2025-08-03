from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertType(Enum):
    AGENT_OFFLINE = "agent_offline"
    AGENT_ERROR = "agent_error"
    HIGH_CPU = "high_cpu"
    HIGH_MEMORY = "high_memory"
    HIGH_DISK = "high_disk"
    COMMAND_FAILED = "command_failed"
    CONNECTION_LOST = "connection_lost"
    SECURITY = "security"
    CUSTOM = "custom"

@dataclass
class Alert:
    """Alert model for system notifications"""
    id: Optional[int] = None
    agent_id: Optional[str] = None
    alert_type: AlertType = AlertType.CUSTOM
    severity: AlertSeverity = AlertSeverity.INFO
    message: str = None
    details: Dict[str, Any] = None
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def resolve(self):
        """Mark alert as resolved"""
        self.is_resolved = True
        self.resolved_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary"""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'alert_type': self.alert_type.value if isinstance(self.alert_type, AlertType) else self.alert_type,
            'severity': self.severity.value if isinstance(self.severity, AlertSeverity) else self.severity,
            'message': self.message,
            'details': self.details,
            'is_resolved': self.is_resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alert':
        """Create alert from dictionary"""
        # Convert enums
        if 'alert_type' in data and isinstance(data['alert_type'], str):
            try:
                data['alert_type'] = AlertType(data['alert_type'])
            except ValueError:
                data['alert_type'] = AlertType.CUSTOM
        
        if 'severity' in data and isinstance(data['severity'], str):
            data['severity'] = AlertSeverity(data['severity'])
        
        # Convert datetime strings to datetime objects
        for field in ['resolved_at', 'created_at']:
            if field in data and data[field] and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        
        return cls(**data)