#!/usr/bin/env python3
"""
DexAgents Backend Server
FastAPI application for Windows PowerShell agent management
"""

import uvicorn
import logging
from app.main import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 