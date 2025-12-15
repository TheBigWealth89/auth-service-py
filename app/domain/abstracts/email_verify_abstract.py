from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
from ...models.email_verification_model import EmailVerificationToken


class IEmailRepository(ABC):
    @abstractmethod
    async def create_token(self, token_id: str, user_id: int, token: str, expires_at: datetime) -> EmailVerificationToken:
        """Create or update a verification and return the stored row."""
        raise NotImplementedError

    @abstractmethod
    async def get_token_by_id(self, user_id: int) -> str:
        """Find token by id and return the token"""
        raise NotImplementedError

    @abstractmethod
    async def get_last_email_sent_at(self, user_id: int) -> Optional[datetime]:
        """Return timestamp of last email sent or None if user has no token"""
        raise NotImplementedError

    @abstractmethod
    async def update_last_email_sent_at(self, user_id: int, timestamp: datetime):
        """Update or create last_email_sent_at for a user."""
        raise NotImplementedError

    @abstractmethod
    async def delete_token(self, token_id: str) -> str:
        """Find and delete token by Id and return the token deleted for a user."""
        raise NotImplementedError
