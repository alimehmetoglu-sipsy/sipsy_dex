from fastapi import APIRouter
from .v1 import agents, commands, system, installer, websocket, auth, settings
from . import metrics

api_router = APIRouter()

# Include all API routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(commands.router, prefix="/commands", tags=["commands"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(installer.router, prefix="/installer", tags=["installer"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(websocket.router, tags=["websocket"])
api_router.include_router(metrics.router, tags=["monitoring"]) 