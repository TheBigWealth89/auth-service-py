from ...repositories.user_repo_postgres import PostgresUserRepository
from ...domain.abstracts.password_hasher_abstract import PasswordHasher
from ...schema.user_dto import UserCreateDTO, UserReadDTO


class UserService:
    def __init__(self, user_repo: PostgresUserRepository, hasher: PasswordHasher):
        self._users = user_repo
        self._hasher = hasher

    async def register(self, dto: UserCreateDTO,) -> UserReadDTO:
        #  normalize
        email = dto.email.strip().lower()

        if len(dto.password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        existing = await self._users.get_user_by_email(email)
        if existing is not None:
            raise ValueError("Email already registered")

        # hash password (expensive; done in threadpool inside hasher)
        hashed = await self._hasher.hash(dto.password)

        created = await self._users.create_user(user_create=dto, password_hash=hashed)

        # return safe DTO
        return UserReadDTO.model_validate(created)
