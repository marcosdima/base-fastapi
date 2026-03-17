from tests.activities.helper import ACTIVITIES_ROUTE, accept_invitation, create_activity, invite_user
from tests.helper import create_default_user, create_secondary_user, post, get


def test_get_public_activities():
    """Test that GET / returns only public activities."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    creator = create_default_user(client)

    # Create 1 private and 2 public activities.
    create_activity(client, creator['token'], 'Private Activity', public=False)
    create_activity(client, creator['token'], 'Public Activity 1', public=True)
    create_activity(client, creator['token'], 'Public Activity 2', public=True)

    # GET public activities without auth (should still work for public ones).
    response = get(client, f'{ACTIVITIES_ROUTE}/')

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    titles = {activity['title'] for activity in body}
    assert titles == {'Public Activity 1', 'Public Activity 2'}
    assert 'Private Activity' not in titles


def test_get_user_activities_includes_private():
    """Test that GET /my returns user's activities including private ones."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    creator = create_default_user(client)

    # Create 1 private and 1 public activity for the creator.
    create_activity(client, creator['token'], 'My Private Activity', public=False)
    create_activity(client, creator['token'], 'My Public Activity', public=True)

    # GET user's own activities.
    response = get(client, f'{ACTIVITIES_ROUTE}/my', token=creator['token'])

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    titles = {activity['title'] for activity in body}
    assert titles == {'My Private Activity', 'My Public Activity'}


def test_get_activities_includes_participants():
    """Test that participants are included in activity responses and updated via invitations."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    creator = create_default_user(client)
    participant1 = create_secondary_user(client)

    # Create another user for the third participant.
    third_user = {
        'username': 'Third User',
        'password': 'Secret@123',
    }
    response_user = post(client, '/api/v1/users/signin', third_user)
    assert response_user.status_code == 201
    invitee2 = response_user.json()

    # Create a public activity.
    activity = create_activity(client, creator['token'], 'Activity with Participants', public=True)

    # Initially, no participants.
    response = get(client, f'{ACTIVITIES_ROUTE}/{activity["id"]}')
    assert response.status_code == 200
    body = response.json()
    assert body['participants'] == []

    # Invite and accept first participant.
    invitation1 = invite_user(client, activity['id'], participant1['id'], creator['token'])
    accept_response1 = accept_invitation(client, invitation1['id'], participant1['token'])
    assert accept_response1.status_code == 200

    # Invite and accept second participant.
    invitation2 = invite_user(client, activity['id'], invitee2['id'], creator['token'])
    accept_response2 = accept_invitation(client, invitation2['id'], invitee2['token'])
    assert accept_response2.status_code == 200

    # Get activity and verify both participants are there.
    response = get(client, f'{ACTIVITIES_ROUTE}/{activity["id"]}')
    assert response.status_code == 200
    body = response.json()
    assert len(body['participants']) == 2
    participant_usernames = {p['username'] for p in body['participants']}
    assert participant_usernames == {'Jane Doe', 'Third User'}


def test_get_user_activities_shows_own_participants():
    """Test that user's own activities show their participants when accessed via /my."""
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    creator = create_default_user(client)
    invitee = create_secondary_user(client)

    # Create activity by creator.
    activity = create_activity(client, creator['token'], 'Activity for Participant Test', public=False)

    # Invite participant and accept.
    invitation = invite_user(client, activity['id'], invitee['id'], creator['token'])
    accept_response = accept_invitation(client, invitation['id'], invitee['token'])
    assert accept_response.status_code == 200

    # Creator gets their own activities and checks participants.
    response = get(client, f'{ACTIVITIES_ROUTE}/my', token=creator['token'])
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    activity_data = body[0]
    assert activity_data['title'] == 'Activity for Participant Test'
    assert len(activity_data['participants']) == 1
    assert activity_data['participants'][0]['username'] == 'Jane Doe'
