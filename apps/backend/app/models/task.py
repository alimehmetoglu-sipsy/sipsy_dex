from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from croniter import croniter
    HAS_CRONITER = True
except ImportError:
    HAS_CRONITER = False

@dataclass
class ScheduledTask:
    """Scheduled task model for automation"""
    id: Optional[int] = None
    name: str = None
    description: Optional[str] = None
    command: str = None
    cron_expression: Optional[str] = None
    agent_id: Optional[str] = None
    group_id: Optional[int] = None
    is_active: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        
        # Calculate next run time if cron expression is provided
        if self.cron_expression and self.next_run is None:
            self.calculate_next_run()
    
    def calculate_next_run(self):
        """Calculate next run time based on cron expression"""
        if self.cron_expression and HAS_CRONITER:
            try:
                base_time = self.last_run if self.last_run else datetime.now()
                cron = croniter(self.cron_expression, base_time)
                self.next_run = cron.get_next(datetime)
            except Exception:
                # Invalid cron expression
                self.next_run = None
        else:
            self.next_run = None
    
    def should_run(self) -> bool:
        """Check if task should run now"""
        if not self.is_active:
            return False
        
        if not self.next_run:
            return False
        
        return datetime.now() >= self.next_run
    
    def mark_completed(self):
        """Mark task as completed and calculate next run"""
        self.last_run = datetime.now()
        self.calculate_next_run()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'command': self.command,
            'cron_expression': self.cron_expression,
            'agent_id': self.agent_id,
            'group_id': self.group_id,
            'is_active': self.is_active,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'should_run': self.should_run(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScheduledTask':
        """Create task from dictionary"""
        # Convert datetime strings to datetime objects
        for field in ['last_run', 'next_run', 'created_at', 'updated_at']:
            if field in data and data[field] and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        
        # Remove derived fields
        data.pop('should_run', None)
        
        return cls(**data)