from tests.helper import get, post, create_default_user, user_default_data


login_route = '/api/v1/users/login'


def test_login_user(client):
    user = create_default_user(client)
    
    response = post(
        client,
        login_route,
        user_default_data
    )
    assert response.status_code == 200

    body = response.json()
    assert body['id'] == user['id']
    assert body['username'] == user['username']
    assert isinstance(body['token'], str)
    assert body['token']


def test_login_user_wrong_password(client):
    create_default_user(client)
    
    modified_data = user_default_data.copy()
    modified_data['password'] = 'rongassword@123'
    response = post(
        client,
        login_route,
        modified_data
    )
    assert response.status_code == 401

    body = response.json()
    assert body['detail'] == 'Invalid credentials'


def test_login_user_username_not_found(client):
    modified_data = user_default_data.copy()
    modified_data['username'] = 'NonExistentUser'

    response = post(
        client,
        login_route,
        modified_data
    )
    assert response.status_code == 404

    body = response.json()
    assert body['detail'] == 'Username not found'