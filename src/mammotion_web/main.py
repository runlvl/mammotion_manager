"""Main application entry point."""

import asyncio
import logging
import sys
from pathlib import Path

import uvicorn

from .app import create_app
from .config import get_settings
from .core.logging import setup_logging


def main() -> None:
    """Main application entry point."""
    settings = get_settings()
    
    # Setup logging first
    setup_logging(settings)
    logger = logging.getLogger(__name__)
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.info("Starting Mammotion Web Control")
    logger.info(f"Configuration: Region={settings.REGION}, Port={settings.PORT}")
    
    try:
        # Create FastAPI app
        app = create_app()
        
        # Run with uvicorn
        uvicorn.run(
            app,
            host=settings.HOST,
            port=settings.PORT,
            log_config=None,  # We handle logging ourselves
            access_log=settings.ACCESS_LOG,
            reload=settings.RELOAD and settings.DEBUG,
        )
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
