import structlog
from fastapi import HTTPException
from ..abstracts.user_abstract import IUserRepository
from ...repositories.postgreSQL.refresh_token_repo import PostgresRefreshTokenRepository
from ...domain.abstracts.password_hasher_abstract import PasswordHasher
from ...schema.auth_dto import LoginDTO, TokenDTO
from ...core.token import create_access_token
from .token_service import TokenService

logger = structlog.get_logger(__name__)


class AuthService:
    def __init__(
        self,
        user_repo: IUserRepository,
        hasher: PasswordHasher,
        refresh_token_repo: PostgresRefreshTokenRepository,
    ):
        self._users = user_repo
        self._hasher = hasher
        self._tokens = refresh_token_repo

    async def login(self, dto: LoginDTO) -> TokenDTO:
        """
        Login user and return TokenDTO
        with access_token and refresh_token (raw)
        """

        email = dto.email.strip().lower()
        user = await self._users.get_user_by_email(email)

        # check if user is verified
        if user and not user.is_verified:
            await logger.awarning(
                "login_failed_unverified",
                user_id=str(user.id),
                email=email,
            )
            raise HTTPException(status_code=403, detail="Email is not verified")

        # generic error to avoid leaking which part failed
        credentials_error = HTTPException(status_code=401, detail="Invalid credentials")
        if user is None:
            await logger.awarning("login_failed_email_not_found", email=email)
            raise credentials_error

        valid = await self._hasher.verify(user.hashed_password, dto.password)
        if not valid:
            await logger.awarning(
                "login_failed_wrong_password",
                user_id=str(user.id),
                email=email,
            )
            raise credentials_error

        # create access token (JWT)
        access_token = create_access_token(sub=str(user.id), role=list([user.role]))

        # create refresh token (opaque raw string)
        token_service = TokenService(self._tokens, self._hasher)
        refresh_token_raw, expires_at = await token_service._issue_refresh_token(user.id)

        await logger.ainfo("login_success", user_id=str(user.id), email=email)

        return TokenDTO(
            access_token=access_token,
            refresh_token_raw=refresh_token_raw,
            expires_at=expires_at,
        )

    async def logout(self, user_id: int):
        """
        Revoke all refresh tokens for the user.
        """
        await self._tokens.revoke_all_refresh_tokens_for_user(user_id)
        await logger.ainfo("logout_success", user_id=str(user_id))
