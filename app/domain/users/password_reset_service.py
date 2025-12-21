import uuid
import secrets
import math
from fastapi import HTTPException, status
from datetime import datetime, timezone, timedelta
from ...schema.user_dto import ResetPasswordDTO
from ..abstracts.password_reset_abstract import IPasswordResetToken
from ..abstracts.user_abstract import IUserRepository
from ..abstracts.password_hasher_abstract import PasswordHasher
from ...schema.user_dto import NewPasswordDTO
from ...core.mailer import ResendMailer


# rate limit 60 secs
RATE_LIMIT_SECONDS = 60


class PasswordResetService:
    def __init__(self, password_reset_repo: IPasswordResetToken, user_repo: IUserRepository, mailer: ResendMailer, hasher: PasswordHasher):
        self._password_reset = password_reset_repo
        self._user_repo = user_repo
        self._mailer = mailer
        self._hasher = hasher

    async def create_and_send_token(self, dto: ResetPasswordDTO):

        # Get user by email
        email = dto.email.strip().lower()
        user = await self._user_repo.get_user_by_email(email)

        if user is None:
            return {"message": "If that email exists, a reset link will be sent."}

        # get the last timestamp email sent
        last = await self._password_reset.get_last_email_sent_at(user.id)

        # check rate  limit
        now = datetime.now(timezone.utc)
        if last and (now - last) < timedelta(seconds=RATE_LIMIT_SECONDS):
            seconds_left = RATE_LIMIT_SECONDS - \
                (now - last).total_seconds()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Please wait {math.ceil(seconds_left)}s before another requesting another email."
            )

        expires_at = now + timedelta(minutes=10)

        # create password reset token
        token_id = uuid.uuid4().hex

        secret = secrets.token_urlsafe(32)
        raw_token = f"{token_id}.{secret}"
        token_hash = await self._hasher.hash(secret)

        await self._password_reset.create_token(
            token_id=token_id,
            user_id=user.id,
            token=token_hash,
            expires_at=expires_at
        )

        # send raw token to user's email
        await self._mailer.send_reset_password_email(user.email, raw_token)


        # update timestamp
        await self._password_reset.update_last_email_sent_at(user.id, now)

    async def verify_token(self, raw_token: str):
        """ Verify the token and return the associated user_id if valid."""
        try:
            token_id, secret = raw_token.split(".", 1)
        except ValueError:
            raise ValueError("Invalid token format")

        record = await self._password_reset.get_token_by_id(token_id)
        if not record:
            raise ValueError("Invalid or expired token")

        if record.expires_at < datetime.now(timezone.utc):
            await self._password_reset.delete_token(token_id)
            raise ValueError("Token has expired")

        if not await self._hasher.verify(record.hashed_token, secret):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
               detail= "Invalid token")

        await self._password_reset.delete_token(token_id)

        return record.user_id

    async def reset_password(self, raw_token: str, dto: NewPasswordDTO, user_repo):
        user_id = await self.verify_token(raw_token)

        password_hash = await self._hasher.hash(dto.new_password)
        await user_repo.update_password(user_id, password_hash)
