from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from ..domain.abstracts.user_abstract import IUserRepository
from ..models.user_model import User


class PostgresUserRepository(IUserRepository):
    def __init__(self, async_session_factory):
        self._session_factory = async_session_factory

    async def get_user_by_email(self, email: str):
        async with self._session_factory() as session:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalars().first()
            # return the ORM User instance (or None)
            return user

    async def create_user(self, user_create, password_hash: str):

        async with self._session_factory() as session:
            user = User(
                name=user_create.name,
                email=user_create.email,
                hashed_password=password_hash
            )
            session.add(user)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()
                # raise so upstream can convert into a 400 or custom error
                raise
            await session.refresh(user)
            return user

    async def mark_verified(self, user_id: int):
        async with self._session_factory() as session:
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            user = result.scalars().first()
            if user:
                user.is_verified = True
                try:
                    await session.commit()
                except Exception:
                    await session.rollback()
                    raise
                await session.refresh(user)
            return user
