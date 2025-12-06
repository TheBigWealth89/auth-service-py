
from fastapi import APIRouter, Depends, HTTPException
from fastapi import Request, Response
from ...schema.auth_dto import LoginDTO, loginResponseDTO
from ...domain.abstracts.password_hasher_abstract import PasswordHasher
from ...domain.auth.auth_service import AuthService
from ...domain.auth.token_service import TokenService
from ...repositories.user_repo_postgres import PostgresUserRepository
from ...repositories.refresh_token_repo import PostgresRefreshTokenRepository
from ...core.token import get_current_user_id
from ..v1.dependencies.get_refresh_token_repo import get_refresh_tokens_repo
# get user repo and hasher dependencies
from ..v1.dependencies.get_user_repo import get_user_repo, get_hasher
router = APIRouter()


@router.post("/auth/login", response_model=loginResponseDTO)
async def login(payload: LoginDTO,
                response: Response,
                user_repo: PostgresUserRepository = Depends(get_user_repo),
                hasher: PasswordHasher = Depends(get_hasher),
                refresh_tokens: PostgresRefreshTokenRepository = Depends(
                    get_refresh_tokens_repo)
                ):
    svc = AuthService(user_repo, hasher, refresh_tokens)
    try:
        token = await svc.login(payload)
        access_token = token.access_token
        refresh_token_raw = token.refresh_token_raw
        # Set http-only cookie for refresh token
        response.set_cookie(
            key="refresh_token",
            value=refresh_token_raw,
            httponly=True,
            secure=False,              # set to True in production with HTTPS
            samesite="none",          # required for cross-site apps
            max_age=60 * 60 * 24 * 7,  # 7 days
            path="/auth/refresh"   # cookie only sent to refresh endpoint
        )

        return {"access_token": access_token}

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal error") from exc


@router.post("/auth/refresh")
async def refresh(
    request: Request,
    response: Response,
        hasher=Depends(get_hasher), refresh_tokens=Depends(get_refresh_tokens_repo)):

    raw_token = request.cookies.get("refresh_token")
    print(raw_token)
    if not raw_token:
        raise HTTPException(status_code=400, detail="refresh_token required")
    svc = TokenService(refresh_tokens, hasher)
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
            secure=False,  # set to True in production with HTTPS
            samesite="none",
            max_age=60 * 60 * 24 * 7,
            path="/auth/refresh"
        )

        return {"access_token": new_access, "expires_at": expires_at}

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/auth/logout")
async def logout(
        response: Response,
        user_id: int = Depends(get_current_user_id),
        refresh_tokens=Depends(get_refresh_tokens_repo), hasher=Depends(get_hasher), user_repo: PostgresUserRepository = Depends(get_user_repo)):

    svc = AuthService(user_repo, hasher, refresh_tokens)
    try:
        await svc.logout(user_id)
        # clear refresh token cookie
        response.delete_cookie(
            key="refresh_token",
            path="/auth/refresh",
        )
        return {"detail": "Logged out successfully"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
