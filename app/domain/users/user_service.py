from ...repositories.user_repo_postgres import PostgresUserRepository
from ...domain.abstracts.password_hasher_abstract import PasswordHasher
from ...schema.user_dto import UserCreateDTO, UserReadDTO
from ..users.email_verification_service import EmailVerificationService


class UserService:
    def __init__(self, user_repo: PostgresUserRepository, hasher: PasswordHasher, email_service: EmailVerificationService):
        self._users = user_repo
        self._hasher = hasher
        self._email_service = email_service

    async def register(self, dto: UserCreateDTO,) -> UserReadDTO:
        #  normalize
        email = dto.email.strip().lower()

        if len(dto.password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # check if user exist but not verified, if user not verified, resend verification email
        existing = await self._users.get_user_by_email(email)
        if existing:
            if not existing.is_verified:
                # resend token
                await self._email_service.create_and_send_token(existing)
                return {"message": "Email already registered but not verified. Verification email resent."}

        # check if user exist and verified
        if existing:
            raise ValueError("Email is already registered")

        # hash password (expensive; done in threadpool inside hasher)
        hashed = await self._hasher.hash(dto.password)

        user = await self._users.create_user(user_create=dto, password_hash=hashed)

        # send verification email
        await self._email_service.create_and_send_token(user)

        # return safe DTO
        return UserReadDTO.model_validate(user)
