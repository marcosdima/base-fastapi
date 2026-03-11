from fastapi import APIRouter
from .users import router as users_router


main_router = APIRouter()
main_router.include_router(users_router, prefix='/users', tags=['users'])