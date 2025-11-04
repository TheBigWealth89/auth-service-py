from .Abstracts import IUserRepository
from .models import User, UserCreate
from asyncpg import pool


class PostgresUserRepository(IUserRepository):
    """
    The concrete implementation of the user repository
    using PostgresSql (asyncpg) for data storage
    """

    def __init__(self, pool: pool):
        self.pool = pool

    async def get_user_by_email(self, email: str) -> User | None:
        print(f"DB: Fetching user by email: {email}")
        return None

    async def create_user(self, user_create: UserCreate) -> User:
        print(f"DB: Creating user with email: {user_create.email}")
        return User(
            id=123,
            name=user_create.name,
            email=user_create.email
        )
