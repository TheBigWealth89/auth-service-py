import uuid
import secrets
import math
from datetime import datetime, timezone, timedelta
from ...repositories.postgreSQL.email_verify_tokens_repo import EmailVerifyTokensRepo
from ...domain.abstracts.password_hasher_abstract import PasswordHasher
from ..abstracts.email_verify_abstract import IEmailRepository
from ...core.mailer import ResendMailer

now = datetime.now(timezone.utc)
# Rate limit time 60 secs
RATE_LIMIT_SECONDS = 60


class EmailVerificationService:
    def __init__(self, verification_repo: IEmailRepository, mailer: ResendMailer, hasher: PasswordHasher):
        self._verification = verification_repo
        self._email = mailer
        self._hasher = hasher

    async def create_and_send_token(self, user):

        # Create a verification token and send it to the user's email.
        token_id = uuid.uuid4().hex

        secret = secrets.token_urlsafe(32)

        raw_token = f"{token_id}.{secret}"

        token_hash = await self._hasher.hash(secret)

        # Get the last time email was sent
        last = await self._verification.get_last_email_sent_at(user.id)

        # check rate limit
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

        # send raw_token to user's email
        # await self._email.send_verification_email(user.email, raw_token)
        print("RAW TOKEN :", raw_token)

        # update timestamp
        await self._verification.update_last_email_sent_at(user.id, now)

    async def verify_token(self, raw_token: str):
        """ Verify the token and return the associated user_id if valid."""
        try:
            token_id, secret = raw_token.split(".", 1)
        except ValueError:
            raise ValueError("Invalid token format")

        record = await self._verification.get_token_by_id(token_id)
        if not record:
            raise ValueError("Invalid or expired token")

        if record.expires_at < datetime.now(timezone.utc):
            await self._verification.delete_token(token_id)
            raise ValueError("Token has expired")

        if not await self._hasher.verify(record.hashed_token, secret):
            raise ValueError("Invalid token")

        await self._verification.delete_token(token_id)

        return record.user_id
