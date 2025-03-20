"""Logging configuration module."""

import logging
from typing import Optional

def setup_logging(level: Optional[int] = logging.WARNING) -> None:
    """
    Set up logging configuration for the application.
    
    Args:
        level: Logging level to use. Defaults to WARNING.
    """
    # Only configure if no handlers exist
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Set specific loggers to WARNING
    loggers = [
        "openai",
        "httpcore",
        "httpx",
        "resume_tailor"
    ]
    
    for logger_name in loggers:
        logging.getLogger(logger_name).setLevel(logging.WARNING) 