from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from ..services.abstract import IUserRepository
from ..models.user_model import User
from ..models.refresh_token_model import RefreshToken


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

    async def save_refresh_token(self, token_id: str, user_id: int, token_hash: str, expires_at: datetime):
        async with self._session_factory() as session:
            rt = RefreshToken(id=token_id, user_id=user_id,
                              token_hash=token_hash, expires_at=expires_at)
            session.add(rt)
            await session.commit()
            await session.refresh(rt)
            return rt

    async def get_refresh_token_by_id(self, token_id: str):
        async with self._session_factory() as session:
            return await session.get(RefreshToken, token_id)

    async def revoke_refresh_token(self, token_id: str):
        async with self._session_factory() as session:
            rt = await session.get(RefreshToken, token_id)
            if rt:
                rt.revoked = True
                await session.commit()

    async def revoke_all_refresh_tokens_for_user(self, user_id: int):
        async with self._session_factory() as session:
            stmt = select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False
            )
            result = await session.execute(stmt)
            tokens = result.scalars().all()

            for t in tokens:
                t.revoked = True

            await session.commit()
