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