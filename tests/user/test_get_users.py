from tests.helper import USERS_ROUTE, create_default_user, get


def test_get_users(client):
    user = create_default_user(client)

    response = get(client, f'{USERS_ROUTE}/users')

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) >= 1

    first_user = body[0]
    assert isinstance(first_user['id'], int)
    assert isinstance(first_user['username'], str)
    assert 'token' not in first_user

    usernames = [item['username'] for item in body]
    assert user['username'] in usernames
