from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request, Response
from ..core.db import AsyncSessionLocal
from ..schema.user_schema import UserCreateDTO, LoginDTO, loginResponseDTO
from ..services.abstract import Argon2PasswordHasher, PasswordHasher
from ..services.user_service import AuthService
from ..repositories.user_repo_postgres import PostgresUserRepository
from ..core.token import get_current_user_id
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


@router.post("/auth/v1/login", response_model=loginResponseDTO)
async def login(payload: LoginDTO,
                response: Response,
                user_repo: PostgresUserRepository = Depends(get_user_repo),
                hasher: PasswordHasher = Depends(get_hasher)
                ):
    svc = AuthService(user_repo, hasher)
    try:
        token = await svc.login(payload)
        access_token = token.access_token
        refresh_token_raw = token.refresh_token_raw
        print("refresh token raw", refresh_token_raw)
        # Set http-only cookie for refresh token
        response.set_cookie(
            key="refresh_token",
            value=refresh_token_raw,
            httponly=True,
            secure=True,              # required for HTTPS
            samesite="none",          # required for cross-site apps
            max_age=60 * 60 * 24 * 7,  # 7 days
            path="/auth/v1/refresh"   # cookie only sent to refresh endpoint
        )

        return {"access_token": access_token}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal error") from exc


@router.post("/auth/v1/refresh")
async def refresh(
        request: Request,
        response: Response,
        user_repo=Depends(get_user_repo), hasher=Depends(get_hasher)):
    raw_token = request.cookies.get("refresh_token")
    if not raw_token:
        raise HTTPException(status_code=400, detail="refresh_token required")
    svc = AuthService(user_repo, hasher)
    try:
        tokens = await svc.refresh_access_token(raw_token)
        new_access = tokens["access_token"]
        new_raw = tokens["refresh_token"]
        expires_at = tokens["expires_at"]

        # rotate refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=new_raw,
            httponly=True,
            secure=True,
            samesite="none",
            max_age=60 * 60 * 24 * 7,
            path="/auth/v1/refresh"
        )

        return {"access_token": new_access, "expires_at": expires_at}

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/auth/v1/logout")
async def logout(
        response: Response,
        user_id: int = Depends(get_current_user_id),
        user_repo=Depends(get_user_repo), hasher=Depends(get_hasher)):

    svc = AuthService(user_repo, hasher)
    try:
        await svc.logout(user_id)
        # clear refresh token cookie
        response.delete_cookie(
            key="refresh_token",
            path="/auth/v1/refresh",
        )
        return {"detail": "Logged out successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
