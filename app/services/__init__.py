from .user_service import UserService


# Services.
user_service: UserService = None


def set_services(session):
    global user_service
    user_service = UserService(session=session)


__all__ = [
    'user_service',
    'set_services'
]