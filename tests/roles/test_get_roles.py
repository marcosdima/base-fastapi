from tests.helper import (
    ROLES_ROUTE,
    clear_test_role_permissions,
    create_default_user,
    get,
    grant_permissions_to_test_role,
)


def test_get_roles(client):
    grant_permissions_to_test_role(['GET_ROLES'])
    user = create_default_user(client)
    response = get(client, ROLES_ROUTE, token=user['token'])

    assert response.status_code == 200
    body = response.json()
    print(body)
    assert isinstance(body, list)
    assert len(body) > 0


def test_get_roles_without_permissions(client):
    clear_test_role_permissions()
    user = create_default_user(client)
    response = get(client, ROLES_ROUTE, token=user['token'])

    assert response.status_code == 403


def test_get_roles_with_malformed_token(client):
    response = get(client, ROLES_ROUTE, token='a.b.c')

    assert response.status_code == 401
    assert response.json()['detail'] == 'Invalid or expired token'
