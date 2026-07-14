import redis.asyncio as redis
from .config import REDIS_URL

# Create a global redis connection pool
redis_client = redis.from_url(REDIS_URL, decode_responses=True)
# get redis client 
async def get_redis():
    """FastAPI Dependency for Redis"""
    yield redis_client
