"""Logging configuration for the application."""

import json
import logging
import os
from datetime import datetime
from typing import Any

import structlog


class JSONFileLogHandler:
    """Handler for JSON file logging."""

    def __init__(self, log_dir: str = "logs"):
        os.makedirs(log_dir, exist_ok=True, mode=0o755)
        self.log_dir = log_dir

    def __call__(self, _, __, event_dict: dict) -> dict:
        """Log the event dictionary to a JSON file."""
        # Create log filename based on date
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(self.log_dir, f"{today}.jsonl")

        # Append log entry to file
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event_dict) + "\n")

        return event_dict


def setup_logging() -> None:
    """Setup logging configuration."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            JSONFileLogHandler(),  # type: ignore
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Get a logger instance with the given name."""
    return structlog.get_logger(name)
