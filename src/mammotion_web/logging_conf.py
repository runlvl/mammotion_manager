"""Logging configuration."""

import logging
import sys


def setup_logging(log_level: str = "INFO") -> None:
    """Setup basic logging."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
