import uuid
import secrets
import structlog
from datetime import datetime, timedelta, timezone
from ...repositories.postgreSQL.refresh_token_repo import PostgresRefreshTokenRepository
from ...domain.abstracts.password_hasher_abstract import PasswordHasher
from ...core.config import REFRESH_TOKEN_EXPIRE_DAYS
from ...core.token import create_access_token

logger = structlog.get_logger(__name__)

now = datetime.now(timezone.utc)


class TokenService:
    def __init__(
        self, refresh_token_repo: PostgresRefreshTokenRepository, hasher: PasswordHasher
    ):
        self._tokens = refresh_token_repo
        self._hasher = hasher

    async def _issue_refresh_token(self, user_id: int):
        token_id = uuid.uuid4().hex
        secret = secrets.token_urlsafe(64)
        raw_token = f"{token_id}.{secret}"

        token_hash = await self._hasher.hash(secret)

        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        await self._tokens.save_refresh_token(
            token_id=token_id,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        await logger.adebug(
            "refresh_token_issued",
            user_id=str(user_id),
            token_id=token_id,
        )

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

        # Attempt to use a non-existent token — treat as suspicious
        if rt is None:
            await logger.acritical(
                "suspicious_activity_unknown_token",
                token_id=token_id,
            )
            await self._tokens.revoke_all_refresh_tokens_for_user(user_id=None)
            raise ValueError("Suspicious activity detected")

        # Attempt to use an already-revoked token — token reuse attack
        if rt.revoked:
            await logger.acritical(
                "token_reuse_detected",
                user_id=str(rt.user_id),
                token_id=token_id,
            )
            await self._tokens.revoke_all_refresh_tokens_for_user(rt.user_id)
            raise ValueError("Refresh token reuse detected")

        # Invalid secret — possible token forgery or replay
        if not await self._hasher.verify(rt.token_hash, secret):
            await logger.awarning(
                "token_hash_mismatch",
                user_id=str(rt.user_id),
                token_id=token_id,
            )
            await self._tokens.revoke_all_refresh_tokens_for_user(rt.user_id)
            raise ValueError("Refresh token misuse detected")

        if rt.expires_at < datetime.now(timezone.utc):
            await logger.ainfo(
                "token_expired",
                user_id=str(rt.user_id),
                token_id=token_id,
            )
            await self._tokens.revoke_refresh_token(token_id)
            raise ValueError("Refresh token expired")

        # Verify secret a second time (defence-in-depth guard)
        valid = await self._hasher.verify(rt.token_hash, secret)
        if not valid:
            await self._tokens.revoke_refresh_token(token_id)
            raise ValueError("Invalid refresh token")

        # Rotate: revoke used token and issue a new one
        await self._tokens.revoke_refresh_token(token_id)
        new_raw, new_expires = await self._issue_refresh_token(rt.user_id)
        access_jwt = create_access_token(sub=str(rt.user_id))

        await logger.ainfo(
            "token_rotation_success",
            user_id=str(rt.user_id),
            old_token_id=token_id,
        )

        return {
            "access_token": access_jwt,
            "refresh_token": new_raw,
            "expires_at": new_expires,
        }
