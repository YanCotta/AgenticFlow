"""
Logging Configuration

This module sets up application-wide logging with different log levels and handlers.
"""
import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from config import settings

# Create logs directory if it doesn't exist
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log file paths
INFO_LOG = LOG_DIR / "app.log"
ERROR_LOG = LOG_DIR / "error.log"
API_LOG = LOG_DIR / "api.log"

# Max log file size (10MB)
MAX_BYTES = 10 * 1024 * 1024
# Number of backup files to keep
BACKUP_COUNT = 5

class RequestIdFilter(logging.Filter):
    """Add request ID to log records if available."""
    
    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = 'N/A'
        return True

def get_logger(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (usually __name__)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    
    # Set log level
    level = getattr(logging, log_level or settings.LOG_LEVEL, logging.INFO)
    logger.setLevel(level)
    
    # Don't propagate to parent loggers
    logger.propagate = False
    
    # Return existing logger if already configured
    if logger.handlers:
        return logger
    
    # Create formatters
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(request_id)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    
    # Create file handlers
    info_handler = RotatingFileHandler(
        INFO_LOG,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(file_formatter)
    info_handler.addFilter(RequestIdFilter())
    
    error_handler = RotatingFileHandler(
        ERROR_LOG,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    error_handler.addFilter(RequestIdFilter())
    
    api_handler = RotatingFileHandler(
        API_LOG,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    api_handler.setLevel(logging.INFO)
    api_handler.setFormatter(file_formatter)
    api_handler.addFilter(RequestIdFilter())
    
    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    
    # Add API handler for API-specific logs
    if name.startswith('api'):
        logger.addHandler(api_handler)
    
    # Configure SQLAlchemy logger if needed
    if name.startswith('sqlalchemy'):
        sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
        sqlalchemy_logger.addHandler(console_handler)
        sqlalchemy_logger.setLevel(logging.WARNING)
    
    return logger

class RequestLogger:
    """Middleware for logging HTTP requests and responses."""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger('api.request')
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        # Generate request ID
        request_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        
        # Log request
        self.logger.info(
            f"Request: {scope['method']} {scope['path']}",
            extra={'request_id': request_id}
        )
        
        # Process request
        async def receive_with_logging():
            message = await receive()
            if message['type'] == 'http.request':
                body = message.get('body', b'').decode('utf-8', 'replace')
                if body:
                    self.logger.debug(
                        f"Request body: {body}",
                        extra={'request_id': request_id}
                    )
            return message
        
        # Log response
        async def send_with_logging(message):
            if message['type'] == 'http.response.start':
                self.logger.info(
                    f"Response: {message['status']}",
                    extra={'request_id': request_id}
                )
            await send(message)
        
        try:
            await self.app(scope, receive_with_logging, send_with_logging)
        except Exception as e:
            self.logger.error(
                f"Request failed: {str(e)}",
                exc_info=True,
                extra={'request_id': request_id}
            )
            raise

def log_api_call(
    logger: logging.Logger,
    endpoint: str,
    method: str,
    status_code: int,
    request_data: Optional[Dict[str, Any]] = None,
    response_data: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
    **kwargs
) -> None:
    """
    Log API calls with consistent format.
    
    Args:
        logger: Logger instance
        endpoint: API endpoint
        method: HTTP method
        status_code: HTTP status code
        request_data: Request data (if any)
        response_data: Response data (if any)
        user_id: ID of the authenticated user (if any)
    """
    log_data = {
        'endpoint': endpoint,
        'method': method,
        'status_code': status_code,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat(),
    }
    
    if request_data:
        log_data['request'] = request_data
    
    if response_data:
        log_data['response'] = response_data
    
    log_data.update(kwargs)
    
    if status_code >= 400:
        logger.error("API Error", extra={'api_data': log_data})
    else:
        logger.info("API Call", extra={'api_data': log_data})
