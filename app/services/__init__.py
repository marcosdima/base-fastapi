from .user_service import UserService
from .roles_service import RoleService


# Services.
user_service: UserService = None
roles_service: RoleService = None


def set_services(session):
    global user_service, roles_service
    user_service = UserService(session=session)
    roles_service = RoleService(session=session)


__all__ = [
    'user_service',
    'roles_service',
    'set_services'
]