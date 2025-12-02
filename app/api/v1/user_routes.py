from fastapi import APIRouter, Depends, HTTPException
from ...core.db import AsyncSessionLocal
from ...schema.user_dto import UserCreateDTO
from ...domain.abstracts.password_hasher_abstract import PasswordHasher
from ...domain.users.user_service import UserService
from ...domain.users.email_verification_service import EmailVerificationService
from ...repositories.user_repo_postgres import PostgresUserRepository
from ..v1.auth_routes import get_user_repo, get_hasher
from ...repositories.email_verify_tokens_repo import EmailVerifyTokensRepo
from ...core.mailer import ResendMailer
router = APIRouter()


def get_verification_repo() -> EmailVerifyTokensRepo:
    return EmailVerifyTokensRepo(AsyncSessionLocal)


def get_email_service() -> EmailVerificationService:
    return EmailVerificationService(AsyncSessionLocal)


def get_mailer() -> ResendMailer:
    return ResendMailer()


@router.post("/auth/register")
async def register(payload: UserCreateDTO, user_repo: PostgresUserRepository = Depends(get_user_repo), hasher: PasswordHasher = Depends(get_hasher), verification_repo: EmailVerifyTokensRepo = Depends(get_verification_repo), mailer: ResendMailer = Depends(get_mailer)):
    email_svc = EmailVerificationService(
        user_repo=user_repo,
        verification_repo=verification_repo,
        email_service=mailer,
        hasher=hasher
    )
    svc = UserService(user_repo, hasher, email_svc)
    try:
        await svc.register(payload)
        return {"message": "Verification email sent to your email address."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/auth/verify-email")
async def verify_email(token: str, user_repo: PostgresUserRepository = Depends(get_user_repo), verification_repo: EmailVerifyTokensRepo = Depends(get_verification_repo), email_service: EmailVerificationService = Depends(get_email_service), hasher: PasswordHasher = Depends(get_hasher)):
    svc = EmailVerificationService(
        user_repo=user_repo,
        verification_repo=verification_repo,
        email_service=email_service,
        hasher=hasher
    )

    record = await verification_repo.find_token(token)
    if not record:
        raise HTTPException(400, "Invalid or expired token")

      # Mark the user verified
    await user_repo.mark_verified(record.user_id)

    try:
        user_id = await svc.verify_token(token)
        # Mark user verified
        await user_repo.mark_verified(user_id)

        return {"message": "Email verified successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
