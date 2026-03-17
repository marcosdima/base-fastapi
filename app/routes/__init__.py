from fastapi import APIRouter
from .users import router as users_router
from .roles import router as roles_router
from .activities import router as activities_router

main_router = APIRouter()
main_router.include_router(users_router, prefix='/users', tags=['users'])
main_router.include_router(roles_router, prefix='/roles', tags=['roles'])
main_router.include_router(activities_router, prefix='/activities', tags=['activities'])