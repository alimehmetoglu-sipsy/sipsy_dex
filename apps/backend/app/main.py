import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import api_router
import asyncio
import threading
import time
from datetime import datetime, timedelta
from .core.database import db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "DexAgents API",
            "version": settings.VERSION,
            "docs": "/docs"
        }
    
    # Background task to check offline agents
    @app.on_event("startup")
    async def start_background_tasks():
        """Start background tasks when the application starts"""
        asyncio.create_task(check_offline_agents())
    
    return app

async def check_offline_agents():
    """Background task to check and mark agents as offline"""
    while True:
        try:
            # Get all agents
            agents = db_manager.get_agents()
            current_time = datetime.now()
            
            for agent in agents:
                agent_id = agent.get('id')
                last_seen_str = agent.get('last_seen')
                current_status = agent.get('status', 'unknown')
                
                if last_seen_str and agent_id:
                    try:
                        last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                        time_diff = (current_time - last_seen).total_seconds()
                        
                        # Mark as offline if no heartbeat for 60 seconds
                        if time_diff > 60 and current_status != 'offline':
                            logger.info(f"Marking agent {agent_id} as offline (last seen: {time_diff:.1f}s ago)")
                            db_manager.update_agent(agent_id, {
                                'status': 'offline',
                                'last_seen': last_seen_str
                            })
                        # Mark as online if heartbeat received recently
                        elif time_diff <= 60 and current_status == 'offline':
                            logger.info(f"Marking agent {agent_id} as online (last seen: {time_diff:.1f}s ago)")
                            db_manager.update_agent(agent_id, {
                                'status': 'online',
                                'last_seen': last_seen_str
                            })
                    except ValueError:
                        # Invalid timestamp, mark as offline
                        if current_status != 'offline':
                            logger.warning(f"Invalid timestamp for agent {agent_id}, marking as offline")
                            db_manager.update_agent(agent_id, {
                                'status': 'offline',
                                'last_seen': last_seen_str
                            })
            
            # Check every 30 seconds
            await asyncio.sleep(30)
            
        except Exception as e:
            logger.error(f"Error in offline agent check: {str(e)}")
            await asyncio.sleep(30)

# Create application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 