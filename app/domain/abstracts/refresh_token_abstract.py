from abc import ABC, abstractmethod
from datetime import datetime


class IOpaqueRefreshToken(ABC):
    @abstractmethod
    async def save_refresh_token(self, token_id: str, user_id: int, token_hash: str, expires_at: datetime) -> str:
        """Save and return refresh token"""
        raise NotImplementedError

    @abstractmethod
    async def get_refresh_token_by_id(self, token_id: str) -> str:
        """Find refresh token by id and return found token"""
        raise NotImplementedError
    @abstractmethod
    async def revoke_refresh_token(self, token_id: str) :
        """Revoke refresh token"""
    @abstractmethod
    async def revoke_all_refresh_tokens_for_user(self, user_id: int):
        """Revoke all tokens for a User."""