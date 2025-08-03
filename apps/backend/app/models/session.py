from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets

@dataclass
class Session:
    """User session model for authentication"""
    id: Optional[str] = None
    user_id: int = None
    token: str = None
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.id is None:
            self.id = secrets.token_urlsafe(16)
        if self.token is None:
            self.token = secrets.token_urlsafe(32)
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.expires_at is None:
            # Default to 24 hours expiration
            self.expires_at = datetime.now() + timedelta(hours=24)
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.now() > self.expires_at
    
    @property
    def time_remaining(self) -> timedelta:
        """Get time remaining until expiration"""
        return self.expires_at - datetime.now()
    
    def extend(self, hours: int = 24):
        """Extend session expiration"""
        self.expires_at = datetime.now() + timedelta(hours=hours)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token': self.token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_expired': self.is_expired,
            'time_remaining_seconds': int(self.time_remaining.total_seconds()) if not self.is_expired else 0
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        """Create session from dictionary"""
        # Convert datetime strings to datetime objects
        for field in ['expires_at', 'created_at']:
            if field in data and data[field] and isinstance(data[field], str):
                data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
        
        # Remove derived fields
        data.pop('is_expired', None)
        data.pop('time_remaining_seconds', None)
        
        return cls(**data)