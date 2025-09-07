"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import get_settings
from .core.logging import setup_logging
from .routers import auth_router, devices_router, ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    settings = get_settings()
    setup_logging(settings)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting Mammotion Web Control")
    
    yield
    
    logger.info("Shutting down Mammotion Web Control")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()
    
    app = FastAPI(
        title="Mammotion Web Control",
        description="Professional web interface for Mammotion robotic lawn mowers",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # Setup templates
    templates_dir = Path(__file__).parent / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))
    app.state.templates = templates
    
    # Setup static files (if directory exists)
    static_dir = Path(__file__).parent / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Include routers
    app.include_router(auth_router.router, prefix="/auth", tags=["authentication"])
    app.include_router(devices_router.router, prefix="/api/devices", tags=["devices"])
    app.include_router(ws_router.router, prefix="/ws", tags=["websocket"])
    
    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "mammotion-web"}
    
    return app


# Create app instance
app = create_app()
