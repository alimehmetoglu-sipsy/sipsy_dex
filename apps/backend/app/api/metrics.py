"""
Metrics collection endpoints for Prometheus monitoring
"""
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from ..core.database import db_manager
from datetime import datetime, timedelta
import psutil

router = APIRouter()

# Metrics storage
metrics_data = {
    "http_requests_total": {},
    "http_request_duration_seconds": {},
    "agent_last_seen_timestamp": {},
    "agent_command_failures_total": {},
    "database_connections": 0,
    "system_info": {}
}

def increment_counter(metric_name: str, labels: Dict[str, str] = None, value: float = 1.0):
    """Increment a counter metric"""
    if labels is None:
        labels = {}
    
    key = "_".join([f"{k}_{v}" for k, v in labels.items()])
    if metric_name not in metrics_data:
        metrics_data[metric_name] = {}
    
    if key not in metrics_data[metric_name]:
        metrics_data[metric_name][key] = 0
    
    metrics_data[metric_name][key] += value

def set_gauge(metric_name: str, labels: Dict[str, str] = None, value: float = 0.0):
    """Set a gauge metric value"""
    if labels is None:
        labels = {}
    
    key = "_".join([f"{k}_{v}" for k, v in labels.items()])
    if metric_name not in metrics_data:
        metrics_data[metric_name] = {}
    
    metrics_data[metric_name][key] = value

def collect_system_metrics():
    """Collect system metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        set_gauge("system_cpu_usage_percent", value=cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        set_gauge("system_memory_usage_bytes", value=memory.used)
        set_gauge("system_memory_total_bytes", value=memory.total)
        set_gauge("system_memory_usage_percent", value=memory.percent)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        set_gauge("system_disk_usage_bytes", value=disk.used)
        set_gauge("system_disk_total_bytes", value=disk.total)
        set_gauge("system_disk_usage_percent", value=(disk.used / disk.total) * 100)
        
    except Exception as e:
        print(f"Error collecting system metrics: {e}")

def collect_agent_metrics():
    """Collect agent-related metrics"""
    try:
        agents = db_manager.get_agents()
        current_time = datetime.now()
        
        online_agents = 0
        offline_agents = 0
        
        for agent in agents:
            agent_id = agent.get('id', 'unknown')
            status = agent.get('status', 'unknown')
            last_seen_str = agent.get('last_seen')
            
            if status == 'online':
                online_agents += 1
            else:
                offline_agents += 1
            
            # Update last seen timestamp
            if last_seen_str:
                try:
                    last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                    timestamp = last_seen.timestamp()
                    set_gauge("agent_last_seen_timestamp", 
                             labels={"agent_id": str(agent_id)}, 
                             value=timestamp)
                except ValueError:
                    pass
        
        set_gauge("agents_online_total", value=online_agents)
        set_gauge("agents_offline_total", value=offline_agents)
        set_gauge("agents_total", value=len(agents))
        
    except Exception as e:
        print(f"Error collecting agent metrics: {e}")

def format_prometheus_metrics() -> str:
    """Format metrics in Prometheus exposition format"""
    collect_system_metrics()
    collect_agent_metrics()
    
    output_lines = []
    
    for metric_name, metric_data in metrics_data.items():
        if metric_name == "system_info":
            continue
            
        # Add metric help and type comments
        if metric_name.endswith("_total"):
            output_lines.append(f"# HELP {metric_name} Total count of {metric_name.replace('_total', '')}")
            output_lines.append(f"# TYPE {metric_name} counter")
        elif "usage" in metric_name or "percent" in metric_name:
            output_lines.append(f"# HELP {metric_name} Current {metric_name}")
            output_lines.append(f"# TYPE {metric_name} gauge")
        else:
            output_lines.append(f"# HELP {metric_name} {metric_name}")
            output_lines.append(f"# TYPE {metric_name} gauge")
        
        if isinstance(metric_data, dict):
            for label_key, value in metric_data.items():
                if label_key:
                    # Parse labels from key
                    label_parts = label_key.split("_")
                    labels_str = ""
                    if len(label_parts) >= 2:
                        labels_list = []
                        for i in range(0, len(label_parts), 2):
                            if i + 1 < len(label_parts):
                                labels_list.append(f'{label_parts[i]}="{label_parts[i+1]}"')
                        if labels_list:
                            labels_str = "{" + ",".join(labels_list) + "}"
                    
                    output_lines.append(f"{metric_name}{labels_str} {value}")
                else:
                    output_lines.append(f"{metric_name} {value}")
        else:
            output_lines.append(f"{metric_name} {metric_data}")
    
    return "\n".join(output_lines)

@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    """Prometheus metrics endpoint"""
    try:
        return format_prometheus_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating metrics: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        agents = db_manager.get_agents()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "agents_count": len(agents)
        }
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

@router.get("/stats")
async def get_system_stats():
    """Get detailed system statistics"""
    try:
        collect_system_metrics()
        collect_agent_metrics()
        
        # Get database stats
        agents = db_manager.get_agents()
        
        stats = {
            "system": {
                "cpu_percent": metrics_data.get("system_cpu_usage_percent", {}).get("", 0),
                "memory_percent": metrics_data.get("system_memory_usage_percent", {}).get("", 0),
                "disk_percent": metrics_data.get("system_disk_usage_percent", {}).get("", 0),
            },
            "agents": {
                "total": len(agents),
                "online": metrics_data.get("agents_online_total", {}).get("", 0),
                "offline": metrics_data.get("agents_offline_total", {}).get("", 0),
            },
            "api": {
                "requests_total": sum(metrics_data.get("http_requests_total", {}).values()),
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

# Middleware function to track HTTP requests
def track_request(request_method: str, request_path: str, status_code: int, duration: float):
    """Track HTTP request metrics"""
    increment_counter("http_requests_total", {
        "method": request_method,
        "path": request_path,
        "status": str(status_code)
    })
    
    # Track duration (simplified histogram)
    duration_key = f"method_{request_method}_path_{request_path.replace('/', '_')}"
    if "http_request_duration_seconds" not in metrics_data:
        metrics_data["http_request_duration_seconds"] = {}
    
    if duration_key not in metrics_data["http_request_duration_seconds"]:
        metrics_data["http_request_duration_seconds"][duration_key] = []
    
    metrics_data["http_request_duration_seconds"][duration_key].append(duration)