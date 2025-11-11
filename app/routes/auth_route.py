from fastapi import APIRouter, Depends, HTTPException
from ..core.db import AsyncSessionLocal
from ..schema.user_schema import UserCreateDTO, LoginDTO, UserReadDTO, TokenDTO
from ..services.abstract import Argon2PasswordHasher, PasswordHasher
from ..services.user_service import AuthService
from ..repositories.user_repo_postgres import PostgresUserRepository

router = APIRouter()


def get_user_repo() -> PostgresUserRepository:
    return PostgresUserRepository(AsyncSessionLocal)


def get_hasher() -> PasswordHasher:
    return Argon2PasswordHasher()


@router.post("/auth/v1/register")
async def register(payload: UserCreateDTO, user_repo: PostgresUserRepository = Depends(get_user_repo), hasher: PasswordHasher = Depends(get_hasher)):
    svc = AuthService(user_repo, hasher)
    try:
        user = await svc.register(payload)
        return {"id": user.id, "name": user.name, "email": user.email}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/auth/v1/login", response_model=TokenDTO)
async def login(payload: LoginDTO,
                user_repo: PostgresUserRepository = Depends(get_user_repo),
                hasher: PasswordHasher = Depends(get_hasher)):
    svc = AuthService(user_repo, hasher)
    try:
        token = await svc.login(payload)
        return token
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal error") from exc
