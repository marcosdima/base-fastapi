from sqlmodel import select

from app.models import Invitation, InvitationStatus, Participate
from tests.activities.helper import (
    ACTIVITIES_ROUTE,
    accept_invitation,
    create_activity,
    invite_user,
    reject_invitation,
)
from tests.helper import create_default_user, create_secondary_user, post


def test_invite_user_success(client):
    creator = create_default_user(client)
    target = create_secondary_user(client)
    activity = create_activity(client, creator['token'], title='Activity for invitations')

    body = invite_user(client, activity['id'], target['id'], creator['token'])

    assert body['to'] == activity['id']
    assert body['target'] == target['id']
    assert body['status'] == InvitationStatus.PENDING


def test_invite_user_only_creator_can_invite(client):
    creator = create_default_user(client)
    non_creator = create_secondary_user(client)
    activity = create_activity(client, creator['token'], title='Activity for invitations')

    response = post(
        client,
        f"{ACTIVITIES_ROUTE}/{activity['id']}/invite/{creator['id']}",
        {},
        token=non_creator['token'],
    )

    assert response.status_code == 403
    assert response.json()['detail'] == 'Only the creator of the activity can send invitations'


def test_reject_invitation(client, db_session):
    creator = create_default_user(client)
    target = create_secondary_user(client)
    activity = create_activity(client, creator['token'], title='Activity for invitations')

    invitation = invite_user(client, activity['id'], target['id'], creator['token'])
    response = reject_invitation(client, invitation['id'], target['token'])

    assert response.status_code == 200
    assert response.json()['detail'] == 'Invitation rejected successfully'

    invitation_db = db_session.get(Invitation, invitation['id'])
    assert invitation_db is not None
    assert invitation_db.status == InvitationStatus.REJECTED


def test_accept_invitation(client, db_session):
    creator = create_default_user(client)
    target = create_secondary_user(client)
    activity = create_activity(client, creator['token'], title='Activity for invitations')

    invitation = invite_user(client, activity['id'], target['id'], creator['token'])
    response = accept_invitation(client, invitation['id'], target['token'])

    assert response.status_code == 200
    assert response.json()['detail'] == 'Invitation accepted successfully'

    invitation_db = db_session.get(Invitation, invitation['id'])
    assert invitation_db is not None
    assert invitation_db.status == InvitationStatus.ACCEPTED

    participation = db_session.exec(
        select(Participate)
        .where(Participate.to == activity['id'])
        .where(Participate.participant == target['id'])
    ).first()
    assert participation is not None


def test_try_to_reject_invitation_twice(client):
    creator = create_default_user(client)
    target = create_secondary_user(client)
    activity = create_activity(client, creator['token'], title='Activity for invitations')

    invitation = invite_user(client, activity['id'], target['id'], creator['token'])

    first_response = reject_invitation(client, invitation['id'], target['token'])
    assert first_response.status_code == 200

    second_response = reject_invitation(client, invitation['id'], target['token'])
    assert second_response.status_code == 400
    assert second_response.json()['detail'] == 'Only pending invitations can be modified'
