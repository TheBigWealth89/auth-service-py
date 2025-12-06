from ....core.db import AsyncSessionLocal
from ....repositories.user_repo_postgres import PostgresUserRepository
from ....domain.abstracts.password_hasher_abstract import PasswordHasher
from ....utils.password_hasher import Argon2PasswordHasher


def get_user_repo() -> PostgresUserRepository:
    return PostgresUserRepository(AsyncSessionLocal)


def get_hasher() -> PasswordHasher:
    return Argon2PasswordHasher()
