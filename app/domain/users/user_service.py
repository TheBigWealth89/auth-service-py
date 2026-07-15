import structlog
from ..abstracts.user_abstract import IUserRepository
from ...domain.abstracts.password_hasher_abstract import PasswordHasher
from ...schema.user_dto import UserCreateDTO, UserReadDTO
from ..users.email_verification_service import EmailVerificationService

logger = structlog.get_logger(__name__)


class UserService:
    def __init__(
        self,
        user_repo: IUserRepository,
        hasher: PasswordHasher,
        email_service: EmailVerificationService,
    ):
        self._users = user_repo
        self._hasher = hasher
        self._email_service = email_service

    async def register(
        self,
        dto: UserCreateDTO,
    ) -> UserReadDTO:
        email = dto.email.strip().lower()

        if len(dto.password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        existing = await self._users.get_user_by_email(email)
        if existing:
            if not existing.is_verified:
                await self._email_service.create_and_send_token(existing)
                await logger.ainfo(
                    "verification_email_resent",
                    user_id=str(existing.id),
                    email=email,
                )
                return {
                    "message": "Email already registered but not verified. Verification email resent."
                }
            else:
                await logger.awarning(
                    "registration_failed_email_exists",
                    email=email,
                )
                raise ValueError("Email is already registered")

        hashed = await self._hasher.hash(dto.password)
        user = await self._users.create_user(user_create=dto, password_hash=hashed)

        await self._email_service.create_and_send_token(user)

        await logger.ainfo(
            "user_registered",
            user_id=str(user.id),
            email=email,
        )

        return UserReadDTO.model_validate(user)
