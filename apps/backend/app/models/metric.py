from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

@dataclass
class AgentMetric:
    """Agent performance metrics model"""
    id: Optional[int] = None
    agent_id: str = None
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    disk_usage: Optional[float] = None
    network_in: Optional[float] = None
    network_out: Optional[float] = None
    process_count: Optional[int] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metric to dictionary"""
        return {
            'id': self.id,
            'agent_id': self.agent_id,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'disk_usage': self.disk_usage,
            'network_in': self.network_in,
            'network_out': self.network_out,
            'process_count': self.process_count,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMetric':
        """Create metric from dictionary"""
        # Convert timestamp string to datetime object
        if 'timestamp' in data and data['timestamp'] and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
        
        return cls(**data)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the metrics"""
        summary = {
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'status': 'healthy'
        }
        
        # Check CPU usage
        if self.cpu_usage is not None:
            summary['cpu_usage'] = self.cpu_usage
            if self.cpu_usage > 90:
                summary['status'] = 'critical'
            elif self.cpu_usage > 80:
                summary['status'] = 'warning'
        
        # Check memory usage
        if self.memory_usage is not None:
            summary['memory_usage'] = self.memory_usage
            if self.memory_usage > 90:
                summary['status'] = 'critical'
            elif self.memory_usage > 80 and summary['status'] == 'healthy':
                summary['status'] = 'warning'
        
        # Check disk usage
        if self.disk_usage is not None:
            summary['disk_usage'] = self.disk_usage
            if self.disk_usage > 90:
                summary['status'] = 'critical'
            elif self.disk_usage > 80 and summary['status'] == 'healthy':
                summary['status'] = 'warning'
        
        return summary