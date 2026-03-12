sign_in_route = '/api/v1/users/signin'
users_route = '/api/v1/users'
login_route = '/api/v1/users/login'
    

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

## Create models.
user_default_data = {
    'username': 'John Doe',
    'password': 'Secret@123',
}


def create_user(client, username: str, password: str) -> dict:
    data = {
        'username': username,
        'password': password,
    }
    response = post(client, sign_in_route, data)
    return response.json()


def create_default_user(client) -> dict:
    response = post(client, sign_in_route, user_default_data)
    if response.status_code == 201:
        return response.json()

    # Tests can share state in the same sqlite file; if the default user already
    # exists, return a valid user payload by logging in with the same credentials.
    body = response.json()
    if response.status_code == 400 and body.get('detail') == 'Username already exists':
        return post(client, login_route, user_default_data).json()

    return body