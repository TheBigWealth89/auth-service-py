from sqlalchemy.future import select
from datetime import datetime, timezone
from ...domain.abstracts.password_reset_abstract import IPasswordResetToken
from ...models.password_reset_tokens import PasswordResetToken


class PasswordResetTokenRepo(IPasswordResetToken):
    def __init__(self, async_session_factory):
        self._async_session_factory = async_session_factory

    async def create_token(
        self, token_id: str, user_id: int, token: str, expires_at: datetime
    ):
        async with self._async_session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
                )
                existing = result.scalar_one_or_none()

                if existing:
                    # Update existing row in-place
                    existing.id = token_id
                    existing.hashed_token = token
                    existing.expires_at = expires_at
                    existing.last_email_sent_at = datetime.now(tz=timezone.utc)
                    token_row = existing
                else:
                    # Create a new row
                    token_row = PasswordResetToken(
                        id=token_id,
                        user_id=user_id,
                        hashed_token=token,
                        expires_at=expires_at,
                        last_email_sent_at=datetime.now(tz=timezone.utc),
                    )
                    session.add(token_row)

            await session.refresh(token_row)
            return token_row

    async def get_token_by_id(self, token_id: str):
        async with self._async_session_factory() as session:
            async with session.begin():
                return await session.get(PasswordResetToken, token_id)

    async def get_last_email_sent_at(self, user_id: int):
        async with self._async_session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(PasswordResetToken.last_email_sent_at).where(
                        PasswordResetToken.user_id == user_id
                    )
                )
                return result.scalar()

    async def update_last_email_sent_at(self, user_id: int, timestamp: datetime):
        async with self._async_session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
                )
                record = result.scalar_one_or_none()

                if record:
                    record.last_email_sent_at = timestamp
                else:
                    record = PasswordResetToken(
                        user_id=user_id, last_email_sent_at=timestamp
                    )
                    session.add(record)

            return record

    async def delete_token(self, token_id: str):
        async with self._async_session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(PasswordResetToken).where(PasswordResetToken.id == token_id)
                )
                token = result.scalars().first()
                if token:
                    await session.delete(token)

            return token
