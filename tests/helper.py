from sqlmodel import select

from app import services
from app.models import Permission, PermissionRole, Role


SIGN_IN_ROUTE = '/api/v1/users/signin'
USERS_ROUTE = '/api/v1/users'
LOGIN_ROUTE = '/api/v1/users/login'
ROLES_ROUTE = '/api/v1/roles'

# Backward-compatible aliases.
sign_in_route = SIGN_IN_ROUTE
users_route = USERS_ROUTE
login_route = LOGIN_ROUTE

# Default identification data reusable across tests.
DEFAULT_USERNAME = 'John Doe'
DEFAULT_PASSWORD = 'Secret@123'
DEFAULT_USER_CREDENTIALS = {
    'username': DEFAULT_USERNAME,
    'password': DEFAULT_PASSWORD,
}

# Secondary user data for tests that require multiple users.
SECONDARY_USERNAME = 'Jane Doe'
SECONDARY_PASSWORD = 'AnotherSecret@123'
SECONDARY_USER_CREDENTIALS = {
    'username': SECONDARY_USERNAME,
    'password': SECONDARY_PASSWORD,
}
    

def __get_authorization_header(token: str) -> dict:
    return {'Authorization': f'Bearer {token}'}


def get(client, url: str, token: str = None):
    headers = __get_authorization_header(token) if token else {}
    return client.get(url, headers=headers)


def post(client, url: str, data: dict, token: str = None):
    headers = __get_authorization_header(token) if token else {}
    return client.post(url, json=data, headers=headers)


def put(client, url: str, data: dict, token: str = None):
    headers = __get_authorization_header(token) if token else {}
    return client.put(url, json=data, headers=headers)


def delete(client, url: str, token: str = None):
    headers = __get_authorization_header(token) if token else {}
    return client.delete(url, headers=headers)

## Backward-compatible alias.
user_default_data = DEFAULT_USER_CREDENTIALS


def create_user(client, username: str, password: str) -> dict:
    data = {
        'username': username,
        'password': password,
    }
    response = post(client, sign_in_route, data)
    return response.json()


def assign_role(client, user_id: int, role_id: int, token: str):
    assign_role_route = f'{ROLES_ROUTE}/{user_id}/assign'
    return post(client, assign_role_route, {'role_id': role_id}, token=token)


def _get_or_create_test_role() -> Role:
    session = services.roles_service.session
    role = session.exec(select(Role).where(Role.name == 'TestRole')).first()

    if role:
        return role

    return services.roles_service.create(
        {
            'name': 'TestRole',
            'description': 'Default role for test users',
        }
    )


def _ensure_default_test_role(user_id: int) -> None:
    role = _get_or_create_test_role()

    services.roles_service.assign_role_to_user(user_id=user_id, new_role_id=role.id)


def grant_permissions_to_test_role(permission_names: list[str]) -> None:
    session = services.roles_service.session
    role = _get_or_create_test_role()

    for permission_name in permission_names:
        permission = session.exec(
            select(Permission).where(Permission.name == permission_name)
        ).first()

        if not permission:
            permission = Permission(
                name=permission_name,
                description=f'Permission used by tests: {permission_name}',
            )
            session.add(permission)
            session.commit()
            session.refresh(permission)

        link = session.exec(
            select(PermissionRole).where(
                PermissionRole.role_id == role.id,
                PermissionRole.permission_id == permission.id,
            )
        ).first()

        if not link:
            session.add(PermissionRole(role_id=role.id, permission_id=permission.id))
            session.commit()


def clear_test_role_permissions() -> None:
    session = services.roles_service.session
    role = session.exec(select(Role).where(Role.name == 'TestRole')).first()
    if not role:
        return

    links = session.exec(
        select(PermissionRole).where(PermissionRole.role_id == role.id)
    ).all()
    for link in links:
        session.delete(link)

    session.commit()


def create_default_user(client) -> dict:
    response = post(client, sign_in_route, user_default_data)
    if response.status_code == 201:
        user = response.json()
        _ensure_default_test_role(user['id'])
        return user

    # Tests can share state in the same sqlite file; if the default user already
    # exists, return a valid user payload by logging in with the same credentials.
    body = response.json()
    if response.status_code == 400 and body.get('detail') == 'Username already exists':
        login_response = post(client, login_route, user_default_data)
        if login_response.status_code != 200:
            raise AssertionError(f'create_default_user failed to login existing user: {login_response.json()}')

        user = login_response.json()
        _ensure_default_test_role(user['id'])
        return user

    raise AssertionError(f'create_default_user failed: status={response.status_code}, body={body}')


def create_secondary_user(client) -> dict:
    response = post(client, sign_in_route, SECONDARY_USER_CREDENTIALS)
    if response.status_code == 201:
        return response.json()

    # Tests can share state in the same sqlite file; if the secondary user already
    # exists, return a valid user payload by logging in with the same credentials.
    body = response.json()
    if response.status_code == 400 and body.get('detail') == 'Username already exists':
        login_response = post(client, login_route, SECONDARY_USER_CREDENTIALS)
        if login_response.status_code != 200:
            raise AssertionError(f'create_secondary_user failed to login existing user: {login_response.json()}')

        return login_response.json()

    raise AssertionError(f'create_secondary_user failed: status={response.status_code}, body={body}')