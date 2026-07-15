import structlog

logger = structlog.get_logger(__name__)


class RateLimitService:
    MAX_ATTEMPTS = 5
    WINDOW_SECONDS = 900  # 15 minutes

    def __init__(self, redis_client):
        self._redis = redis_client

    def _get_key(self, ip: str, email: str) -> str:
        return f"rate_limit:login:{ip}:{email}"

    async def check_and_increment(self, ip: str, email: str):
        key = self._get_key(ip, email)

        # INCR creates the key with value 1 if it doesn't exist, and increments otherwise.
        attempts = await self._redis.incr(key)

        # If this is the very first attempt, set the expiration window.
        if attempts == 1:
            await self._redis.expire(key, self.WINDOW_SECONDS)

        await logger.adebug(
            "rate_limit_incremented",
            ip=ip,
            email=email,
            attempt_count=attempts,
        )

        if attempts > self.MAX_ATTEMPTS:
            await logger.awarning(
                "rate_limit_exceeded",
                ip=ip,
                email=email,
                attempt_count=attempts,
            )
            raise ValueError("Rate limit exceeded")

    async def clear_limit(self, ip: str, email: str):
        key = self._get_key(ip, email)
        await self._redis.delete(key)
        await logger.ainfo(
            "rate_limit_cleared",
            ip=ip,
            email=email,
        )
