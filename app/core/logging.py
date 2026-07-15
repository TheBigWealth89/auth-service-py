import logging
import structlog


def configure_logging(log_level: str = "INFO") -> None:
    """
    Configure structlog as the single logging pipeline for the entire application.
    Silences uvicorn's default loggers to prevent duplicate log lines.
    """

    # --- 1. Silence uvicorn's built-in loggers ---
    # uvicorn registers three loggers. Clearing their handlers and disabling
    # propagation ensures no plain-text lines escape alongside our JSON output.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvi_logger = logging.getLogger(name)
        uvi_logger.handlers.clear()
        uvi_logger.propagate = False

    # --- 2. Route stdlib logging through structlog ---
    # Any library that uses the standard `logging` module (SQLAlchemy, httpx, etc.)
    # will have its output captured and formatted as structured JSON.
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    # --- 3. Configure structlog processors ---
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,      # injects request_id, user_id, etc.
            structlog.stdlib.add_log_level,               # adds "level" field
            structlog.stdlib.add_logger_name,             # adds "logger" field
            structlog.processors.TimeStamper(fmt="iso"),  # adds ISO-8601 timestamp
            structlog.processors.StackInfoRenderer(),     # renders stack traces
            structlog.processors.format_exc_info,         # renders exception info
            structlog.processors.JSONRenderer(),          # final JSON output
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        # stdlib.LoggerFactory creates real logging.Logger objects which have
        # the .name attribute that add_logger_name requires.
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
