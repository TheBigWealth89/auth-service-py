from ....repositories.refresh_token_repo import PostgresRefreshTokenRepository
from ....core.db import AsyncSessionLocal


def get_refresh_tokens_repo() -> PostgresRefreshTokenRepository:
    return PostgresRefreshTokenRepository(AsyncSessionLocal)
