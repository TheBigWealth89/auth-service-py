from ..domain.abstracts.password_hasher_abstract import PasswordHasher
import asyncio

class Argon2PasswordHasher(PasswordHasher):
    """
    Set up Argon2 password hasher
    Argon2 wrapper (argon2-cffi is synchronous we call it in a threadpool)
    It inherits from PasswordHasher therefore in must implements all the abstract methods hash & verify
    """

    def __init__(self, *, time_cost: int = 2, memory_cost: int = 65536, parallelism: int = 1):
        # Lazy import so module can be read even if argon2 isn't installed in the current environment
        from argon2 import PasswordHasher as _PH, Type
        # Using Type.ID => Argon2id
        self._ph = _PH(time_cost=time_cost, memory_cost=memory_cost,
                      parallelism=parallelism, type=Type.ID)

    async def hash(self, plain: str) -> str:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._ph.hash, plain)

    async def verify(self, hashed: str, plain: str) -> bool:
        loop = asyncio.get_running_loop()

        def _verify():
            try:
                return self._ph.verify(hashed, plain)
            except Exception:
                return False
        return await loop.run_in_executor(None, _verify)
