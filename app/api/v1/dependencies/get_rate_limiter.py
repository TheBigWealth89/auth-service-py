from fastapi import Request, Depends, HTTPException
from ....schema.auth_dto import LoginDTO
from ....core.redis import get_redis
from ....domain.auth.rate_limit_service import RateLimitService

async def enforce_login_rate_limit(
    request: Request, 
    payload: LoginDTO, 
    redis_client = Depends(get_redis)
) -> RateLimitService:
    ip = request.client.host
    email = payload.email.strip().lower()
    
    svc = RateLimitService(redis_client)
    try:
        await svc.check_and_increment(ip, email)
        return svc
    except ValueError:
        raise HTTPException(
            status_code=429, 
            detail="Too many login attempts. Please try again in 15 minutes."
        )
