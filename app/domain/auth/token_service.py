import uuid
import secrets
from datetime import datetime, timedelta, timezone
from ...repositories.postgreSQL.refresh_token_repo import PostgresRefreshTokenRepository
from ...domain.abstracts.password_hasher_abstract import PasswordHasher
from ...core.config import REFRESH_TOKEN_EXPIRE_DAYS
from ...core.token import create_access_token

now = datetime.now(timezone.utc)


class TokenService:
    def __init__(self, refresh_token_repo: PostgresRefreshTokenRepository, hasher: PasswordHasher):
        self._tokens = refresh_token_repo
        self._hasher = hasher

    async def _issue_refresh_token(self, user_id: int):
        token_id = uuid.uuid4().hex                   # stable id we can look up
        # raw secret to give client
        secret = secrets.token_urlsafe(64)
        raw_token = f"{token_id}.{secret}"            # raw token format

        # hash secret for storage (use your Argon2 hasher)
        token_hash = await self._hasher.hash(secret)

        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        await self._tokens.save_refresh_token(token_id=token_id, user_id=user_id, token_hash=token_hash, expires_at=expires_at)

        return raw_token, expires_at

    async def refresh_access_token(self, raw_token: str):
        """
        raw_token is the string the client sends back: "token_id.secret"
        Returns new access token and new refresh token (rotated).
        """
        try:
            token_id, secret = raw_token.split(".", 1)
        except ValueError:
            raise ValueError("Invalid token format")

        rt = await self._tokens.get_refresh_token_by_id(token_id)
        
        # Attempt to use a non-existent token
        if rt is None:
            await self._tokens.revoke_all_refresh_tokens_for_user(user_id=None)
            raise ValueError("Suspicious activity detected")

        # Attempt to use a revoked token
        if rt.revoked:
            await self._tokens.revoke_all_refresh_tokens_for_user(rt.user_id)
            raise ValueError("Refresh token reuse detected")

            # Invalid secret someone is guessing or replaying
        if not await self._hasher.verify(rt.token_hash, secret):
            await self._tokens.revoke_all_refresh_tokens_for_user(rt.user_id)
            raise ValueError("Refresh token misuse detected")

        if rt.expires_at < datetime.now(timezone.utc):
            # expired: revoke and reject
            await self._tokens.revoke_refresh_token(token_id)
            raise ValueError("Refresh token expired")

        # verify secret against stored hash
        valid = await self._hasher.verify(rt.token_hash, secret)
        if not valid:
            # token invalid — possible theft: revoke the token and maybe all _tokens for user
            await self._tokens.revoke_refresh_token(token_id)
            raise ValueError("Invalid refresh token")

        # rotate: revoke used token and issue a new one
        await self._tokens.revoke_refresh_token(token_id)

        new_raw, new_expires = await self._issue_refresh_token(rt.user_id)

        # create new access token (JWT) for user.id (keep access token code)
        access_jwt = create_access_token(sub=str(rt.user_id))

        return {"access_token": access_jwt, "refresh_token": new_raw, "expires_at": new_expires}
