from sqlmodel import select

from ..models import Activity, Invitation, InvitationStatus, Participate, User
from .base_service import BaseService


class ActivityService(BaseService[Activity]):
    def __init__(self, session):
        super().__init__(Activity, session)


    def _get_activity_with_participants(self, activity: Activity) -> dict:
        participants_statement = (
            select(User)
                .join(Participate, Participate.participant == User.id)
                .where(Participate.to == activity.id)
        )
        participants = self.session.exec(participants_statement).all()
        activity_dict = activity.model_dump()
        # Convert participants to UserPublic format (id, username only)
        activity_dict['participants'] = [
            {'id': p.id, 'username': p.username} for p in participants
        ]
        return activity_dict


    def get_all(self, include_disabled=False):
        activities = super().get_all(include_disabled)
        return [self._get_activity_with_participants(activity) for activity in activities]


    def get_user_activities(self, user_id: int):
        statement = (
            select(Activity)
                .where(Activity.creator_id == user_id)
                .where(Activity.disabled == False)
        )
        activities = self.session.exec(statement).all()
        return [self._get_activity_with_participants(activity) for activity in activities]
    

    def get_public_activities(self):
        statement = (
            select(Activity)
                .where(Activity.public == True)
                .where(Activity.disabled == False)
        )
        activities = self.session.exec(statement).all()
        return [self._get_activity_with_participants(activity) for activity in activities]


    def get_activity_with_participants(self, activity_id: int):
        activity = self.get_by_id(activity_id)
        if not activity:
            return None
        return self._get_activity_with_participants(activity)
        

    def send_invitation(self, target: int, to: int) -> Invitation:
        invitation = Invitation(target=target, to=to)

        self.session.add(invitation)
        self.session.commit()
        self.session.refresh(invitation)

        return invitation
    

    def is_peding(self, target: int, to: int) -> bool:
        statement = (
            select(Invitation)
                .where(Invitation.target == target)
                .where(Invitation.to == to)
                .where(Invitation.status == InvitationStatus.PENDING)
        )
        return self.session.exec(statement).first() is not None


    def reject_invitation(self, invitation_id: int) -> Invitation | None:
        invitation = self.session.get(Invitation, invitation_id)

        invitation.status = InvitationStatus.REJECTED
        self.session.add(invitation)
        self.session.commit()
        self.session.refresh(invitation)

        return invitation


    def accept_invitation(self, invitation_id: int) -> Invitation | None:
        invitation = self.session.get(Invitation, invitation_id)

        # Update the invitation status to accepted.
        invitation.status = InvitationStatus.ACCEPTED
        self.session.add(invitation)

        # Create participation record for the user in the activity.
        participation = Participate(participant=invitation.target, to=invitation.to)
        self.session.add(participation)

        # Save the changes to the database and refresh the invitation instance.
        self.session.commit()
        self.session.refresh(invitation)

        return invitation
    

    def get_user_invitations(self, user_id: int) -> list[Invitation]:
        statement = (
            select(Invitation)
                .where(Invitation.to == user_id)
                .where(Invitation.status == InvitationStatus.PENDING)
        )
        return self.session.exec(statement).all()
    
    
    def get_invitation_by_id(self, invitation_id: int) -> Invitation | None:
        return self.session.get(Invitation, invitation_id)