from google.oauth2 import id_token
from google.auth.transport import requests
from ...repositories.user_repo_postgres import PostgresUserRepository
from ...repositories.refresh_token_repo import PostgresRefreshTokenRepository
from ...utils.password_hasher import PasswordHasher
from ...domain.auth.token_service import TokenService
from ...core.token import create_access_token
from ...core.config import GOOGLE_CLIENT_ID


class GoogleAuthService:

    def __init__(self, users: PostgresUserRepository, tokens: PostgresRefreshTokenRepository, hasher: PasswordHasher):
        self._users = users
        self._tokens = tokens
        self._hasher = hasher

    async def login_with_google(self, google_id_token: str):

        try:
            # Verify Google token
            payload = id_token.verify_oauth2_token(
                google_id_token,
                requests.Request(),
                GOOGLE_CLIENT_ID
            )
        except Exception:
            raise ValueError("Invalid Google token")

        email = payload.get("email")
        name = payload.get("name")
        sub = payload.get("sub")  # Google's user ID

        user = await self._users.get_user_by_email(email)

        if not user:
            # create account if not exists
            user = await self._users.create_google_user(
                email=email,
                google_id=sub,
                name=name
            )
        # create access token (JWT)
        access_token = create_access_token(sub=str(user.id), role=list(
            [user.role]))

        # create refresh token (opaque raw string)
        token_service = TokenService(self._tokens, self._hasher)
        refresh_token_raw = await token_service._issue_refresh_token(user.id)

        # return tokens and user info
        return access_token, refresh_token_raw, user
