"""
SwarmDroid Multi-Agent AI Backend Entrypoint
FastAPI application with WebSocket streaming, CORS, and orchestrator lifecycle.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from .config import settings
from .api.routes import router
from .orchestration.swarm_orchestrator import swarm_orchestrator
from .websocket.connection_manager import ws_manager

logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))
logger = logging.getLogger("swarmdroid.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing SwarmDroid Multi-Agent Engine...")
    
    # Wire orchestrator events directly to WebSocket broadcast
    async def forward_event_to_websocket(event_type: str, data: dict):
        await ws_manager.broadcast(event_type, data)
        
    swarm_orchestrator.set_event_listener(forward_event_to_websocket)
    logger.info("SwarmDroid Engine Ready: 'One companion. An entire swarm of intelligence.'")
    yield
    logger.info("Shutting down SwarmDroid Backend...")


app = FastAPI(
    title="SwarmDroid Multi-Agent API",
    description="Real-time Multi-Agent AI Ecosystem with 3D Companion Mascot for Android",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "app": "SwarmDroid",
        "tagline": "One companion. An entire swarm of intelligence.",
        "version": "1.0.0",
        "status": "operational",
        "agents_active": len(swarm_orchestrator.get_all_agents())
    }


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=settings.host, port=settings.port, reload=True)
