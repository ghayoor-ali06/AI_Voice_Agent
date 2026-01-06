"""
FastAPI application for AI Voice Agent.
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .websocket.handlers import handle_voice_agent_connection
from .openai_client.session_manager import session_manager
from .tools.registry import setup_tools
from .utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting AI Voice Agent application")
    logger.info(f"Model: {settings.openai_model}")
    logger.info(f"Audio: {settings.audio_sample_rate}Hz, {settings.audio_channels} channel(s)")

    # Set up tools
    setup_tools()
    logger.info(f"Registered tools successfully")

    # Start session cleanup loop
    await session_manager.start_cleanup_loop(interval_seconds=300)

    yield

    # Shutdown
    logger.info("Shutting down AI Voice Agent application")

    # Stop session cleanup
    await session_manager.stop_cleanup_loop()

    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="AI Voice Agent",
    description="Real-time voice agent powered by OpenAI GPT-4o Realtime API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model": settings.openai_model,
        "audio_config": {
            "sample_rate": settings.audio_sample_rate,
            "channels": settings.audio_channels,
            "chunk_size": settings.audio_chunk_size
        },
        "active_sessions": session_manager.active_session_count
    }


@app.websocket("/ws/voice")
async def voice_agent_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for voice agent communication.

    Args:
        websocket: WebSocket connection
    """
    await handle_voice_agent_connection(websocket)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "AI Voice Agent API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "websocket": "/ws/voice"
        },
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
