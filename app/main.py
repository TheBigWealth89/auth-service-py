from fastapi import FastAPI
from .api.v1 import auth_routes, user_routes

app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description="Learning Python with FastAPI and SOLID principles",
)

app.include_router(auth_routes.router, tags=["Auth"])
app.include_router(user_routes.router, tags=["Auth"])
