from fastapi import APIRouter, Depends, HTTPException
from ...schema.user_dto import UserCreateDTO
from ...domain.abstracts.password_hasher_abstract import PasswordHasher
from ...domain.users.user_service import UserService
from ...repositories.user_repo_postgres import PostgresUserRepository
from ..v1.auth_routes import get_user_repo, get_hasher
router = APIRouter()


@router.post("/auth/register")
async def register(payload: UserCreateDTO, user_repo: PostgresUserRepository = Depends(get_user_repo), hasher: PasswordHasher = Depends(get_hasher)):
    svc = UserService(user_repo, hasher)
    try:
        user = await svc.register(payload)
        return {"id": user.id, "name": user.name, "email": user.email}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
