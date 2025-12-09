from sqlalchemy.future import select
from datetime import datetime
from ..models.email_verification_model import EmailVerificationToken


class EmailVerifyTokensRepo:
    def __init__(self, async_session_factory):
        self._async_session_factory = async_session_factory

    async def create_token(self, token_id: str, user_id: int, token: str, expires_at):
        async with self._async_session_factory() as session:
            email_token = EmailVerificationToken(id=token_id,
                                                 user_id=user_id, hashed_token=token, expires_at=expires_at

                                                 )
            session.add(email_token)
            try:
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            await session.refresh(email_token)
            return email_token

    async def get_token_by_id(self, token_id: str):
        async with self._async_session_factory() as session:
            return await session.get(EmailVerificationToken, token_id)

    async def get_last_email_sent_at(self, user_id: int):
        async with self._async_session_factory() as session:
            result = await session.execute(
                select(EmailVerificationToken.last_email_sent_at).
                where(EmailVerificationToken.user_id == user_id)
            )

            return result.scalar()

    async def update_last_email_sent_at(self, user_id: int, timestamp: datetime):
        async with self._async_session_factory() as session:
            result = session.execute(
                select(EmailVerificationToken).where(
                    EmailVerificationToken.user_id == user_id)
            )

            record = result.scalar_one_or_none()
            if record:
                # update existing row
                record.last_email_sent_at = timestamp
            else:
                # insert new row
                record = EmailVerificationToken(
                    user_id=user_id,
                    last_email_sent_at=timestamp

                )
                session.add(record)
                await session.commit()

    async def delete_token(self, token_id: str):
        async with self._async_session_factory() as session:
            result = await session.execute(
                select(EmailVerificationToken).where(
                    EmailVerificationToken.id == token_id)
            )
            email_token = result.scalars().first()
        try:
            if email_token:
                await session.delete(email_token)
                await session.commit()
        except Exception:
            await session.rollback()
            raise
        return email_token
