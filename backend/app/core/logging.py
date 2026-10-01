"""
Structured logging initialization module using structlog.
Provides JSON formatted logs in production and human-friendly colored logging in development/demo.
"""
import sys
import logging
import structlog
from typing import Any, Dict
from app.core.config import settings


def setup_logging() -> None:
    """Initialize structured logging configuration for FastAPI, Uvicorn, and app components."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if settings.is_demo_mode or settings.DEBUG:
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Silence noisy standard library loggers
    for noisy_module in ["uvicorn.access", "sqlalchemy.engine", "httpcore", "httpx"]:
        logging.getLogger(noisy_module).setLevel(logging.WARNING)


def get_logger(name: str = "hotel_revenue") -> structlog.stdlib.BoundLogger:
    """Obtain a structured logger instance bound to a specific module name."""
    return structlog.get_logger(name)
