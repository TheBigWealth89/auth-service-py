# It defines the 'contract' for what our repository must do
from abc import ABC, abstractmethod

"""
The interface (Abstract Base Class ) for a user repository.
Defines the contract that all user repositories must follow.
"""
class IUserRepository(ABC):

    @abstractmethod
    async def get_user_by_email(self, email:str) -> User | None:
        """ FInd user by their email addresses"""
        pass

    async def create_user(self, user_create: CreateUser) -> User :
        """ Creates a user in the database."""
        pass

