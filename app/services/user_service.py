from fastapi import HTTPException
from ..repositories.user_repo_postgres import PostgresUserRepository
from ..schema.user_schema import LoginDTO, UserCreateDTO, UserReadDTO
from ..services.abstract import PasswordHasher


class AuthService:
    def __init__(self, user_repo: PostgresUserRepository, hasher: PasswordHasher):
        self._users = user_repo
        self._hasher = hasher

    async def register(self, dto: UserCreateDTO) -> UserReadDTO:
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

    async def login(self, dto: LoginDTO) -> UserCreateDTO:
        email = dto.email.strip().lower()
        user = await self._users.get_user_by_email(email)
        # generic error to avoid leaking which part failed
        credentials_error = HTTPException(
            status_code=401, detail="Invalid credentials")

        if user is None:
            raise credentials_error

         # user is an ORM instance; hashed password on attribute `hashed_password`
        valid = await self._hasher.verify(user.hashed_password, dto.password)
        if not valid:
            raise credentials_error
        return UserReadDTO.model_validate(user)
