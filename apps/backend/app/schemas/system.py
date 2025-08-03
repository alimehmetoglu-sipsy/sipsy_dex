from typing import Dict
from pydantic import BaseModel

class SystemInfo(BaseModel):
    hostname: str
    os_version: str
    cpu_usage: float
    memory_usage: float
    disk_usage: Dict[str, float] 