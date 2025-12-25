"""
Structured logging configuration for Find My Journal API.
Provides JSON logging for production and colored console output for development.
"""
import logging
import sys
from typing import Optional
from functools import lru_cache

from .config import get_settings


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging in production.
    Outputs logs in a format easily parsed by log aggregators.
    """

    def format(self, record: logging.LogRecord) -> str:
        import json
        from datetime import datetime

        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data

        return json.dumps(log_data)


class ConsoleFormatter(logging.Formatter):
    """
    Colored console formatter for development.
    Uses ANSI colors for better readability.
    """

    COLORS = {
        "DEBUG": "\033[36m",    # Cyan
        "INFO": "\033[32m",     # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",    # Red
        "CRITICAL": "\033[35m", # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)

        # Format: [LEVEL] logger_name - message
        formatted = f"{color}[{record.levelname}]{self.RESET} {record.name} - {record.getMessage()}"

        # Add exception info if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


def setup_logging(
    level: Optional[str] = None,
    use_json: Optional[bool] = None
) -> None:
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               Defaults to settings.log_level or INFO.
        use_json: Whether to use JSON format. Defaults to True in production
                  (when debug=False), False in development.
    """
    settings = get_settings()

    # Determine log level
    if level is None:
        level = getattr(settings, "log_level", "INFO")
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Determine formatter
    if use_json is None:
        use_json = not settings.debug

    # Create formatter
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = ConsoleFormatter()

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


@lru_cache(maxsize=128)
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        Configured logger instance.

    Example:
        from app.core.logging import get_logger

        logger = get_logger(__name__)
        logger.info("Processing search request", extra={"query": query})
    """
    return logging.getLogger(name)
