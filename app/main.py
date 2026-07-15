from fastapi import FastAPI
from .core.config import LOG_LEVEL
from .core.logging import configure_logging

# Configure structured logging first — before any other import that might log
configure_logging(log_level=LOG_LEVEL)

from .core.middleware import RequestIDMiddleware
from .api.v1 import auth_routes, user_routes

app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description="Learning Python with FastAPI and SOLID principles",
)

# Request ID middleware must be the outermost layer so every log line
# produced during a request automatically carries the request_id
app.add_middleware(RequestIDMiddleware)

app.include_router(auth_routes.router, tags=["Auth"])
app.include_router(user_routes.router, tags=["Auth"])
