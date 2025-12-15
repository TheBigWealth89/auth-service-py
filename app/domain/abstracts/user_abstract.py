from abc import ABC, abstractmethod
from typing import Optional
from ...models.user_model import User
from ...schema.user_dto import UserCreateDTO


class IUserRepository(ABC):
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Return a User or None by email."""
        raise NotImplementedError

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Return a User or None by user_id"""
        raise NotImplementedError

    @abstractmethod
    async def create_user(self, user_create: UserCreateDTO, password_hash: str) -> User:
        """Create a user and return the created User."""
        raise NotImplementedError

    @abstractmethod
    async def mark_verified(self, user_id: int) -> Optional[User]:
        """Mark a user verified and return the verified User."""
    @abstractmethod
    async def create_google_user(self, email: str, google_id: str, name: str) -> User:
        """Create a user with Google and return created User"""
