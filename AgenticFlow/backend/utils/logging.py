"""
Logging configuration for AgenticFlow.

This module configures structured logging with structlog and standard logging.
"""
import logging
import sys
import os
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional

import structlog
from structlog.types import EventDict, WrappedLogger

# Configure structlog processors
timestamper = structlog.processors.TimeStamper(fmt="iso")

# Common processor for adding log level and logger name
add_log_level = structlog.stdlib.add_log_level
add_logger_name = structlog.stdlib.add_logger_name

# Configure JSON formatter for structured logging
def json_formatter(logger: WrappedLogger, name: str, event_dict: EventDict) -> str:
    """Format the event dict as a JSON string."""
    # Ensure the event_dict is JSON serializable
    for key, value in event_dict.items():
        if isinstance(value, (datetime,)):
            event_dict[key] = value.isoformat()
    
    # Add timestamp if not present
    if "timestamp" not in event_dict:
        event_dict["timestamp"] = datetime.utcnow().isoformat()
    
    # Add process and thread info
    event_dict["process"] = os.getpid()
    event_dict["thread"] = os.getpid()  # In most cases, this is sufficient
    
    return json.dumps(event_dict, ensure_ascii=False)

# Configure console formatter for development
def console_formatter(logger: WrappedLogger, name: str, event_dict: EventDict) -> str:
    """Format the event dict for console output."""
    timestamp = event_dict.pop("timestamp", None)
    if timestamp:
        timestamp = timestamp.split(".")[0].replace("T", " ")
    
    level = event_dict.pop("level", "-").upper()
    logger_name = event_dict.pop("logger", name)
    event = event_dict.pop("event", "")
    
    # Format the remaining key-value pairs
    extra = ""
    if event_dict:
        extra = " " + " ".join(f"{k}={v!r}" for k, v in event_dict.items())
    
    return f"{timestamp} [{level:5s}] {logger_name}: {event}{extra}"

def configure_logging(level: Optional[str] = None, json_logs: Optional[bool] = None) -> None:
    """
    Configure logging for the application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: Whether to output logs as JSON (default: False in development, True in production)
    """
    # Default to INFO level if not specified
    log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Determine if we should use JSON logs (default: False in development, True in production)
    if json_logs is None:
        json_logs = os.getenv("JSON_LOGS", "false").lower() == "true"
    
    # Common processors for both console and JSON output
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        timestamper,
    ]
    
    # Configure structlog
    structlog.configure(
        processors=shared_processors + [
            # Prepare the event dict for the final formatter
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # Format the output
            json_formatter if json_logs else console_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure the standard library logging
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add a console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(handler)
    
    # Configure specific loggers
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.error").handlers = []
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if log_level == "DEBUG" else logging.WARNING
    )
    logging.getLogger("sqlalchemy.pool").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.orm").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("gunicorn").handlers = []
    
    # Set up structlog for uvicorn
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = []
        logging_logger.propagate = True
    
    # Log the configuration
    logger = structlog.get_logger(__name__)
    logger.info("Logging configured", level=log_level, json_logs=json_logs)
