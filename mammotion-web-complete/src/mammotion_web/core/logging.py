"""Logging configuration and setup."""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Any, Dict

import structlog

from ..config import Settings


def setup_logging(settings: Settings) -> None:
    """Setup structured logging with configurable output format."""
    
    # Create logs directory if specified
    if settings.LOG_FILE:
        settings.LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" 
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL)
        ),
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    handlers = ["console"]
    if settings.LOG_FILE:
        handlers.append("file")
    
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter" if settings.LOG_FORMAT == "json" else "logging.Formatter",
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "json" if settings.LOG_FORMAT == "json" else "standard",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "mammotion_web": {
                "level": settings.LOG_LEVEL,
                "handlers": handlers,
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": handlers,
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO" if settings.ACCESS_LOG else "WARNING",
                "handlers": handlers,
                "propagate": False,
            },
        },
        "root": {
            "level": "WARNING",
            "handlers": handlers,
        },
    }
    
    # Add file handler if specified
    if settings.LOG_FILE:
        logging_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "json" if settings.LOG_FORMAT == "json" else "standard",
            "filename": str(settings.LOG_FILE),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
    
    logging.config.dictConfig(logging_config)
    
    # Get logger and log startup - FIX: Use proper message format
    logger = logging.getLogger("mammotion_web.core.logging")
    log_file_info = str(settings.LOG_FILE) if settings.LOG_FILE else "console only"
    logger.info(
        f"Logging configured - Level: {settings.LOG_LEVEL}, Format: {settings.LOG_FORMAT}, Output: {log_file_info}"
    )
