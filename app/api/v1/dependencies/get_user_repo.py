from ....core.db import AsyncSessionLocal
from ....domain.abstracts.user_abstract import IUserRepository
from ....domain.abstracts.password_hasher_abstract import PasswordHasher
from ....utils.password_hasher import Argon2PasswordHasher
from ....repositories.user_repo_postgres import PostgresUserRepository


def get_user_repo() -> IUserRepository:
    return PostgresUserRepository(AsyncSessionLocal)


def get_hasher() -> PasswordHasher:
    return Argon2PasswordHasher()
