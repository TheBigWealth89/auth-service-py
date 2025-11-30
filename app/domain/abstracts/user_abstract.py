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
    async def create_user(self, user_create: UserCreateDTO, password_hash: str) -> User:
        """Create a user and return the created User."""
        raise NotImplementedError


