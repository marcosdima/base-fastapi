from tests.helper import post


ACTIVITIES_ROUTE = '/api/v1/activities'


def build_activity_payload(title: str, public: bool = True, participants_capacity: int = 10) -> dict:
    return {
        'title': title,
        'description': f'Description for {title}',
        'participants_capacity': participants_capacity,
        'public': public,
    }


def create_activity(client, token: str, title: str, public: bool = True, participants_capacity: int = 10) -> dict:
    response = post(
        client,
        f'{ACTIVITIES_ROUTE}/create',
        build_activity_payload(title=title, public=public, participants_capacity=participants_capacity),
        token=token,
    )
    assert response.status_code == 201
    return response.json()


def invite_user(client, activity_id: int, target_user_id: int, creator_token: str) -> dict:
    response = post(
        client,
        f'{ACTIVITIES_ROUTE}/{activity_id}/invite/{target_user_id}',
        {},
        token=creator_token,
    )
    assert response.status_code == 201
    return response.json()


def accept_invitation(client, invitation_id: int, user_token: str):
    return post(client, f'{ACTIVITIES_ROUTE}/invitations/{invitation_id}/accept', {}, token=user_token)


def reject_invitation(client, invitation_id: int, user_token: str):
    return post(client, f'{ACTIVITIES_ROUTE}/invitations/{invitation_id}/reject', {}, token=user_token)
