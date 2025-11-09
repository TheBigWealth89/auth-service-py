from fastapi import FastAPI
from app.routes import auth_route

app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description="Learning Python with FastAPI and SOLID principles",
)

app.include_router(auth_route.router, tags=["Auth"])
