"""
Logging configuration for the application.
Sets up loggers with appropriate handlers and formatters.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

from loguru import logger

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """
    Intercepts standard logging messages and redirects them to Loguru.
    """
    
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        
        # Find caller from where the logged message originated
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    """
    Configure logging for the application.
    
    Sets up Loguru logger with console and file handlers based on settings.
    Also intercepts standard library logging.
    """
    # Remove default loguru handler
    logger.remove()
    
    # Add console handler
    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    logger.add(sys.stderr, format=log_format, level=settings.logging.level)
    
    # Add file handler if configured
    if settings.logging.file:
        log_file = Path(settings.logging.file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            str(log_file),
            rotation="10 MB",
            retention="1 month",
            format=log_format,
            level=settings.logging.level,
            compression="zip"
        )
    
    # Intercept standard library logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    
    # Intercept uvicorn and fastapi logs
    for logger_name in ("uvicorn", "uvicorn.access", "fastapi"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
    
    logger.info("Logging configured successfully")


def get_logger(name: Optional[str] = None):
    """
    Get a logger instance with the given name.
    
    Args:
        name: Logger name, typically the module name
        
    Returns:
        A Loguru logger instance
    """
    return logger.bind(name=name or "app")


# Set up logging when module is imported
setup_logging()