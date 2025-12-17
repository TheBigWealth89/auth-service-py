from ....core.db import AsyncSessionLocal
from ....domain.abstracts.user_abstract import IUserRepository
from ....domain.abstracts.password_hasher_abstract import PasswordHasher
from ....domain.abstracts.password_reset_abstract import IPasswordResetToken
from ....utils.password_hasher import Argon2PasswordHasher
from ....repositories.postgreSQL.user_repo_postgres import PostgresUserRepository
from ....repositories.postgreSQL.password_reset_repo import PasswordResetTokenRepo


def get_user_repo() -> IUserRepository:
    return PostgresUserRepository(AsyncSessionLocal)


def get_hasher() -> PasswordHasher:
    return Argon2PasswordHasher()

def get_pw_reset_repo() -> IPasswordResetToken:
    return PasswordResetTokenRepo(AsyncSessionLocal)
