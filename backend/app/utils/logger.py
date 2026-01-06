"""
Logging configuration for the application.
"""
import logging
import sys
from typing import Optional
from ..config import settings


def setup_logger(name: Optional[str] = None, level: Optional[str] = None) -> logging.Logger:
    """
    Set up and configure logger.

    Args:
        name: Logger name (default: root logger)
        level: Log level (default: from settings)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or __name__)

    # Set log level
    log_level = level or settings.log_level
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logger.level)

    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger


# Default application logger
logger = setup_logger("voice_agent")
