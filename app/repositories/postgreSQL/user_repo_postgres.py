from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from ...domain.abstracts.user_abstract import IUserRepository
from ...models.user_model import User


class PostgresUserRepository(IUserRepository):
    def __init__(self, async_session_factory):
        self._session_factory = async_session_factory

    async def get_user_by_email(self, email: str):
        async with self._session_factory() as session:
            async with session.begin():
                stmt = select(User).where(User.email == email)
                result = await session.execute(stmt)
                return result.scalars().first()

    async def get_user_by_id(self, user_id: str):
        async with self._session_factory() as session:
            async with session.begin():
                stmt = select(User).where(User.id == user_id)
                result = await session.execute(stmt)
                return result.scalars().first()

    async def create_user(self, user_create, password_hash: str):
        async with self._session_factory() as session:
            async with session.begin():
                user = User(
                    name=user_create.name,
                    email=user_create.email,
                    hashed_password=password_hash,
                )
                session.add(user)
                # begin() auto-commits on success, auto-rolls back on any exception.
                # IntegrityError (duplicate email) will bubble up naturally.
            # Refresh AFTER the transaction closes to reload DB-generated fields.
            await session.refresh(user)
            return user

    async def mark_verified(self, user_id: int):
        async with self._session_factory() as session:
            async with session.begin():
                stmt = select(User).where(User.id == user_id)
                result = await session.execute(stmt)
                user = result.scalars().first()
                if user:
                    user.is_verified = True
            if user:
                await session.refresh(user)
            return user

    async def create_google_user(self, email: str, google_id: str, name: str):
        async with self._session_factory() as session:
            async with session.begin():
                user = User(
                    name=name,
                    email=email,
                    google_id=google_id,
                    is_verified=True,  # OAuth users are considered verified
                )
                session.add(user)
            await session.refresh(user)
            return user

    async def update_password(self, user_id: int, hashed_password: str):
        async with self._session_factory() as session:
            async with session.begin():
                stmt = select(User).where(User.id == user_id)
                result = await session.execute(stmt)
                user = result.scalar_one_or_none()
                if not user:
                    return None
                user.hashed_password = hashed_password
            await session.refresh(user)
            return user
