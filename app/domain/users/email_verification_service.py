import uuid
import secrets
from datetime import datetime, timezone, timedelta
from ...repositories.user_repo_postgres import PostgresUserRepository
from ...repositories.email_verify_tokens_repo import EmailVerifyTokensRepo
from ...domain.abstracts.password_hasher_abstract import PasswordHasher
from ...core.mailer import ResendMailer


class EmailVerificationService:
    def __init__(self, user_repo: PostgresUserRepository, verification_repo: EmailVerifyTokensRepo, email_service: ResendMailer, hasher: PasswordHasher):
        self._users = user_repo
        self._verification = verification_repo
        self._email = email_service
        self._hasher = hasher

    async def create_and_send_token(self, user):
        """ Create a verification token and send it to the user's email."""
        token_id = uuid.uuid4().hex

        secret = secrets.token_urlsafe(32)

        raw_token = f"{token_id}.{secret}"

        token_hash = await self._hasher.hash(secret)

        await self._verification.create_token(
            user_id=user.id,
            token=token_hash,
            expires_at= datetime.now(timezone.utc) + timedelta(minutes=10)
        )
        await self._email.send_verification_email(user.email, raw_token)
