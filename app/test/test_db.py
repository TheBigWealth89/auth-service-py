import asyncio
import hashlib
from sqlalchemy import select
from ..core.db import engine, AsyncSessionLocal, Base
from ..models.user_model import User

async def create_tables():
    # Creates tables based on Base metadata (runs in a synchronous context via run_sync)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def test_insert_and_query():
    async with AsyncSessionLocal() as session:
        try:
            # create a quick test hash so NOT NULL constraint is satisfied
            plain_password = "testpassword"  # test-only password
            hashed_password = hashlib.sha256(plain_password.encode()).hexdigest()

            # create + add
            user = User(name="wealth", email="wealth@example.com", hashed_password=hashed_password)
            session.add(user)
            await session.commit()           # flush & commit to DB
            await session.refresh(user)      # refresh to get DB-assigned fields e.g., id

            # query
            result = await session.execute(select(User).where(User.email == "wealth@example.com"))
            user_from_db = result.scalars().first()
            print("Loaded:", user_from_db.id, user_from_db.name, user_from_db.email)

        except Exception as exc:
            # rollback on error and re-raise so you still see the trace in CI/dev
            await session.rollback()
            print("Test failed, rolled back. Error:", exc)
            raise

async def main():
    try:
        await create_tables()
        await test_insert_and_query()
    finally:
        await engine.dispose()  # cleanly close the connection pool

if __name__ == "__main__":
    asyncio.run(main())
