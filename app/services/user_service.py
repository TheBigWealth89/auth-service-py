from fastapi import HTTPException
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from ..core.config import REFRESH_TOKEN_EXPIRE_DAYS
from ..repositories.user_repo_postgres import PostgresUserRepository
from ..schema.user_schema import LoginDTO, UserCreateDTO, UserReadDTO, TokenDTO
from ..services.abstract import PasswordHasher
from ..core.token import create_access_token

now = datetime.now(timezone.utc)


class AuthService:
    def __init__(self, user_repo: PostgresUserRepository, hasher: PasswordHasher):
        self._users = user_repo
        self._hasher = hasher

    async def register(self, dto: UserCreateDTO,) -> UserReadDTO:
        #  normalize
        email = dto.email.strip().lower()

        if len(dto.password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        existing = await self._users.get_user_by_email(email)
        if existing is not None:
            raise ValueError("Email already registered")

        # hash password (expensive; done in threadpool inside hasher)
        hashed = await self._hasher.hash(dto.password)

        created = await self._users.create_user(user_create=dto, password_hash=hashed)

        # return safe DTO
        return UserReadDTO.model_validate(created)

    async def login(self, dto: LoginDTO) -> TokenDTO:
        """
    Login user and return TokenDTO 
    with access_token and refresh_token (raw)
        """

        email = dto.email.strip().lower()
        user = await self._users.get_user_by_email(email)
        # generic error to avoid leaking which part failed
        credentials_error = HTTPException(
            status_code=401, detail="Invalid credentials")
        if user is None:
            raise credentials_error

        valid = await self._hasher.verify(user.hashed_password, dto.password)
        if not valid:
            raise credentials_error

        # create access token (JWT)
        access_token = create_access_token(sub=str(user.id), role=list(
            [user.role]))
        # create refresh token (opaque raw + store hash)
        refresh_token_raw, expires_at = await self._issue_refresh_token(user.id)

        return TokenDTO(access_token=access_token, refresh_token_raw=refresh_token_raw, expires_at=expires_at)

    async def _issue_refresh_token(self, user_id: int):
        token_id = uuid.uuid4().hex                   # stable id we can look up
        # raw secret to give client
        secret = secrets.token_urlsafe(64)
        raw_token = f"{token_id}.{secret}"            # raw token format

        # hash secret for storage (use your Argon2 hasher)
        token_hash = await self._hasher.hash(secret)

        expires_at = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        await self._users.save_refresh_token(token_id=token_id, user_id=user_id, token_hash=token_hash, expires_at=expires_at)

        return raw_token, expires_at

    async def refresh_access_token(self, raw_token: str):
        """
        raw_token is the string the client sends back : "token_id.secret"
        Returns new access token and new refresh token (rotated).
        """
        try:
            token_id, secret = raw_token.split(".", 1)
        except ValueError:
            raise ValueError("Invalid token format")

        rt = await self._users.get_refresh_token_by_id(token_id)
        if rt is None or rt.revoked:
            raise ValueError("Invalid or revoked refresh token")

        if rt.expires_at < now:
            # expired: revoke and reject
            await self._users.revoke_refresh_token(token_id)
            raise ValueError("Refresh token expired")

        # verify secret against stored hash
        valid = await self._hasher.verify(rt.token_hash, secret)
        if not valid:
            # token invalid — possible theft: revoke the token and maybe all tokens for user
            await self._users.revoke_refresh_token(token_id)
            raise ValueError("Invalid refresh token")

        # rotate: revoke used token and issue a new one
        await self._users.revoke_refresh_token(token_id)

        new_raw, new_expires = await self._issue_refresh_token(rt.user_id)

        # create new access token (JWT) for user.id (keep access token code)
        access_jwt = create_access_token(sub=str(rt.user_id))

        return {"access_token": access_jwt, "refresh_token": new_raw, "expires_at": new_expires}
