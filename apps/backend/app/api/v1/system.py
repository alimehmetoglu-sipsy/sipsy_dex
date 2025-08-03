from fastapi import APIRouter, HTTPException, Depends
from ...schemas.system import SystemInfo
from ...core.auth import verify_token
import psutil
import platform
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/info", response_model=SystemInfo)
async def get_system_info(token: str = Depends(verify_token)):
    """Get system information"""
    try:
        return await get_system_info_internal()
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get system information")

@router.get("/health")
async def api_health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "DexAgents API"}

async def get_system_info_internal() -> SystemInfo:
    """Internal function to get system information"""
    try:
        # Get hostname
        hostname = platform.node()
        
        # Get OS version
        os_version = f"{platform.system()} {platform.release()}"
        
        # Get CPU usage
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # Get memory usage
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Get disk usage
        disk_usage = {}
        for partition in psutil.disk_partitions():
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disk_usage[partition.device] = (partition_usage.used / partition_usage.total) * 100
            except PermissionError:
                continue
        
        return SystemInfo(
            hostname=hostname,
            os_version=os_version,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=disk_usage
        )
    except Exception as e:
        logger.error(f"Error getting system information: {str(e)}")
        raise 