from tests.helper import get, post


default_data = {
    'username': 'John Doe',
    'password': 'Secret@123',
}

signin_route = '/api/v1/users/signin'
login_route = '/api/v1/users/login'
users_route = '/api/v1/users'


def test_create_user(client):
    response = post(client, signin_route, default_data)

    assert response.status_code == 201
    body = response.json()
    assert body['id'] == 1
    assert body['username'] == 'John Doe'
    assert isinstance(body['token'], str)
    assert body['token']


def test_create_users_wrong_data(client):
    bad_passwords = [
        {
            'password': 'short',
            'loc': ['body', 'password'],
            'type': 'string_too_short',
            'msg': 'String should have at least 8 characters'
        },
        {
            'password': 'secret123@',
            'loc': ['body', 'password'],
            'type': 'value_error',
            'msg': 'Password must contain at least one uppercase letter'
        },
        {
            'password': 'SECRET123@',
            'loc': ['body', 'password'],
            'type': 'value_error',
            'msg': 'Password must contain at least one lowercase letter'
        },
        {
            'password': 'SecretPwd@',
            'loc': ['body', 'password'],
            'type': 'value_error',
            'msg': 'Password must contain at least one digit'
        },
        {
            'password': 'Secret123',
            'loc': ['body', 'password'],
            'type': 'value_error',
            'msg': 'Password must contain at least one special character (@$!%*?&)'
        }
    ]

    for case in bad_passwords:
        response = post(
            client,
            signin_route,
            {'username': 'John Doe', 'password': case['password']}
        )

        assert response.status_code == 422
        body = response.json()

        assert body['detail'][0]['loc'] == case['loc']
        assert body['detail'][0]['type'] == case['type']
        assert case['msg'] in body['detail'][0]['msg']