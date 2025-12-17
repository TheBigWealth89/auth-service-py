import uuid
import secrets
import math
from datetime import datetime, timezone, timedelta
from ..abstracts.password_reset_abstract import IPasswordResetToken
from ..abstracts.password_hasher_abstract import PasswordHasher
from ...core.mailer import ResendMailer


now = datetime.now(timezone)
# rate limit 60 secs
RATE_LIMIT_SECONDS = 60


class PasswordResetService:
    def __init__(self, password_reset_repo: IPasswordResetToken, mailer: ResendMailer, hasher: PasswordHasher):
        self.password_reset = password_reset_repo
        self.mailer = mailer
        self._hasher = hasher

    async def create_and_send_token(self, user):
        # create password reset token and send it user's email
        token_id = uuid.uuid4().hex

        secret = secrets.token_urlsafe(32)
        raw_token = f"{token_id}.{secret}"
        token_hash = await self._hasher.hash(secret)

        # get the last timestamp email sent
        last = await self._password_reset.get_last_email_sent_at(user.id)

        # check rate  limit
        if last and (datetime.now(timezone.utc) - last) < timedelta(seconds=RATE_LIMIT_SECONDS):
            seconds_left = RATE_LIMIT_SECONDS - \
                (datetime.now(timezone.utc) - last).total_seconds()
            raise ValueError(
                f"Please wait {math.ceil(seconds_left)}s before another requesting another email."
            )

        expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
        await self._verification.create_token(
            token_id=token_id,
            user_id=user.id,
            token=token_hash,
            expires_at=expires_at
        )

        # send raw token to user's email
        await self._mailer.send_reset_password_email(user.email, raw_token)

        print("Raw token:", raw_token)

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
            raise ValueError("Invalid token")

        await self._password_reset.delete_token(token_id)

        return record.user_id

    async def reset_password(self, raw_token: str, new_password: str, user_repo):
        user_id = await self.verify_token(raw_token)

        password_hash = await self._hasher.hash(new_password)
        await user_repo.update_password(user_id, password_hash)
