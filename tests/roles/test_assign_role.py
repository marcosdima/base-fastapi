from sqlmodel import select

from app.models import Role
from tests.helper import (
    ROLES_ROUTE,
    assign_role,
    create_default_user,
    delete,
    grant_permissions_to_test_role,
)


def _get_or_create_test_role(db_session):
    role = db_session.exec(select(Role).where(Role.name == 'TestRole')).first()
    if role:
        return role

    role = Role(name='TestRole', description='Role used by role tests')
    db_session.add(role)
    db_session.commit()
    db_session.refresh(role)
    return role


def test_assign_role(client, db_session):
    grant_permissions_to_test_role(['ASSIGN_ROLES'])
    user = create_default_user(client)
    role = _get_or_create_test_role(db_session)

    response = assign_role(client, user['id'], role.id, user['token'])

    assert response.status_code == 201
    body = response.json()
    assert body['user_id'] == user['id']
    assert body['role_id'] == role.id


def test_remove_role(client, db_session):
    grant_permissions_to_test_role(['ASSIGN_ROLES', 'REMOVE_USER_ROLE'])
    user = create_default_user(client)
    role = _get_or_create_test_role(db_session)
    remove_role_route = f"{ROLES_ROUTE}/{user['id']}/remove"

    assign_response = assign_role(client, user['id'], role.id, user['token'])
    assert assign_response.status_code == 201

    remove_response = delete(client, remove_role_route, token=user['token'])
    assert remove_response.status_code == 200
    assert remove_response.json()['detail'] == 'Role removed successfully'
