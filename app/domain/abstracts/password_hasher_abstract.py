from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    async def hash(self, plain: str) -> str:
        """Takes plain password and returns hashed string."""
        raise NotImplementedError

    @abstractmethod
    async def verify(self, hashed: str, plain: str) -> bool:
        """Check whether plain matches hashed"""
        raise NotImplementedError
