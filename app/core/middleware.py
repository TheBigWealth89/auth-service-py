import uuid
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Generates a unique request_id for every incoming HTTP request and binds
    it to the structlog context. This ensures every log line emitted during
    the request lifecycle automatically carries the same request_id, making
    it trivial to correlate all events from a single request in Datadog or Loki.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())

        # Bind context variables that will be auto-merged into every log line
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        )

        response = await call_next(request)

        await logger.ainfo(
            "request_completed",
            status_code=response.status_code,
        )

        # Clear context after the response so it doesn't leak into the next request
        structlog.contextvars.clear_contextvars()
        return response
