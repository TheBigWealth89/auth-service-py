
from ....domain.abstracts.refresh_token_abstract import IOpaqueRefreshToken 
from ....repositories.refresh_token_repo import PostgresRefreshTokenRepository
from ....core.db import AsyncSessionLocal


def get_refresh_tokens_repo() -> IOpaqueRefreshToken:
    return PostgresRefreshTokenRepository(AsyncSessionLocal)
