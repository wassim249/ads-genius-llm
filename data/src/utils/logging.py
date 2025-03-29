"""Logging configuration for the data pipeline."""

import json
import logging
import os
from datetime import datetime
from typing import Any, Optional

import structlog


class JSONFileLogHandler:
    """Handler for JSON file logging."""

    def __init__(self, log_dir: str = "logs/data_pipeline"):
        """Initialize the JSON file log handler.

        Args:
            log_dir: Directory to store log files.
        """
        os.makedirs(log_dir, exist_ok=True, mode=0o755)
        self.log_dir = log_dir

    def __call__(self, _, __, event_dict: dict) -> dict:
        """Log the event dictionary to a JSON file.

        Args:
            _: Logger (not used)
            __: Method name (not used)
            event_dict: Event dictionary to log

        Returns:
            The event dictionary
        """
        # Create log filename based on date
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"{today}.jsonl")

        # Append log entry to file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_dict) + "\n")

        return event_dict


class PipelineLoggerFactory:
    """Factory for creating pipeline loggers."""

    @staticmethod
    def create_logger(name: Optional[str] = None, log_level: int = logging.INFO) -> Any:
        """Create a logger with the given name and log level.

        Args:
            name: Logger name
            log_level: Logging level

        Returns:
            A configured logger
        """
        return structlog.get_logger(name)


def setup_logging(log_level: int = logging.INFO, console: bool = True, file: bool = True) -> None:
    """Setup logging configuration for the data pipeline.

    Args:
        log_level: The logging level
        console: Whether to log to console
        file: Whether to log to file
    """
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.dev.set_exc_info,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if file:
        processors.append(JSONFileLogHandler())

    if console:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: Optional[str] = None) -> Any:
    """Get a logger instance with the given name.

    Args:
        name: Logger name

    Returns:
        A configured logger
    """
    return structlog.get_logger(name)


# Initialize logging with default settings
setup_logging()
