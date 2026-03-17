from .user_service import UserService
from .roles_service import RoleService
from .activity_service import ActivityService


# Services.
user_service: UserService = None
roles_service: RoleService = None
activity_service: ActivityService = None

def set_services(session):
    global user_service, roles_service, activity_service
    user_service = UserService(session=session)
    roles_service = RoleService(session=session)
    activity_service = ActivityService(session=session)


__all__ = [
    'user_service',
    'roles_service',
    'activity_service',
    'set_services'
]