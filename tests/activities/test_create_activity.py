from sqlmodel import select

from app.models import Activity
from tests.activities.helper import ACTIVITIES_ROUTE, create_activity
from tests.helper import create_default_user, post


def test_create_activity(client, db_session):
    user = create_default_user(client)

    body = create_activity(client, user['token'], title='Activity 1', public=True)

    assert body['title'] == 'Activity 1'
    assert body['description'] == 'Description for Activity 1'
    assert body['public'] is True

    created = db_session.exec(select(Activity).where(Activity.id == body['id'])).first()
    assert created is not None
    assert created.creator_id == user['id']


def test_more_than_5_activities(client):
    user = create_default_user(client)

    for i in range(1, 6):
        response = post(
            client,
            f'{ACTIVITIES_ROUTE}/create',
            {
                'title': f'Activity {i}',
                'description': f'Description for Activity {i}',
                'participants_capacity': 10,
                'public': True,
            },
            token=user['token'],
        )
        assert response.status_code == 201

    response = post(
        client,
        f'{ACTIVITIES_ROUTE}/create',
        {
            'title': 'Activity 6',
            'description': 'Description for Activity 6',
            'participants_capacity': 10,
            'public': True,
        },
        token=user['token'],
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'User cannot create more than 5 activities'
