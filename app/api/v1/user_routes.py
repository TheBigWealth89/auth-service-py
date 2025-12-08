from fastapi import Response
from fastapi import APIRouter, Depends, HTTPException

from ...schema.user_dto import UserCreateDTO  # user creation DTO
from ...domain.abstracts.password_hasher_abstract import PasswordHasher
from ...domain.users.user_service import UserService
from ...domain.users.google_oauth_service import GoogleAuthService
from ...domain.users.email_verification_service import EmailVerificationService
from ...domain.auth.token_service import TokenService  # refresh toke service
from ...repositories.user_repo_postgres import PostgresUserRepository
from ...repositories.email_verify_tokens_repo import EmailVerifyTokensRepo
from ...core.mailer import ResendMailer
from ...core.token import create_access_token 
from ...repositories.refresh_token_repo import PostgresRefreshTokenRepository
from .dependencies.get_verification import get_verification_repo, get_mailer
from ..v1.dependencies.get_refresh_token_repo import get_refresh_tokens_repo
from ..v1.dependencies.get_user_repo import get_user_repo, get_hasher
router = APIRouter()


@router.post("/auth/register")
async def register(payload: UserCreateDTO,
                   user_repo: PostgresUserRepository = Depends(get_user_repo),
                   hasher: PasswordHasher = Depends(get_hasher),
                   verification_repo: EmailVerifyTokensRepo = Depends(
                       get_verification_repo),
                   mailer: ResendMailer = Depends(get_mailer)):

    email_svc = EmailVerificationService(
        verification_repo=verification_repo,
        mailer=mailer,
        hasher=hasher
    )
    svc = UserService(user_repo, hasher, email_svc)
    try:
        await svc.register(payload)
        return {"message": "Verification email sent to your email address."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/auth/verify-email")
async def verify_email(token: str,
                       response: Response,
                       user_repo: PostgresUserRepository = Depends(
                           get_user_repo),
                       verification_repo: EmailVerifyTokensRepo = Depends(
                           get_verification_repo),
                       mailer: ResendMailer = Depends(get_mailer),
                       hasher: PasswordHasher = Depends(get_hasher),
                       token_repo: PostgresRefreshTokenRepository = Depends(get_refresh_tokens_repo
                                                                            )):
    svc = EmailVerificationService(
        verification_repo=verification_repo,
        mailer=mailer,
        hasher=hasher
    )

    rt = TokenService(refresh_token_repo=token_repo, hasher=hasher)

    try:
        user_id = await svc.verify_token(token)
        user = await user_repo.get_user_by_id(user_id)
        # Mark user verified
        await user_repo.mark_verified(user_id)

        # Login user after verification
        access_token = create_access_token(sub=str(user.id), role=[user.role])
        refresh_token_raw = await rt._issue_refresh_token(user.id)

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
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/auth/google")
async def google_auth(
    token: str,
    response: Response,
    user_repo: PostgresUserRepository = Depends(get_user_repo),
    token_service: TokenService = Depends(get_refresh_tokens_repo),
    hasher: PasswordHasher = Depends(get_hasher)
):
    google_svc = GoogleAuthService(
        user_repo=user_repo, token_service=token_service, hasher=hasher)

    try:
        access, refresh_token_raw, user = await google_svc.login_with_google(token)
        # Set cookies
        response.set_cookie(
            key="refresh_token",
            value=refresh_token_raw,
            httponly=True,
            secure=False,              # set to True in production with HTTPS
            samesite="none",          # required for cross-site apps
            max_age=60 * 60 * 24 * 7,  # 7 days
            path="/auth/refresh"   # cookie only sent to refresh endpoint
        )

        return {
            "access_token": access,
            "user": {"id": user.id, "email": user.email}
        }
    except ValueError as e:
        raise HTTPException(400, str(e))
