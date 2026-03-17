from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.models.activities.invitation import InvitationStatus, Invitation
from .dependencies.auth import parse_token_and_get_user
from .. import services
from .users import UserPublic


router = APIRouter()


class Activity(BaseModel):
    id: int = Field(1, ge=1, json_schema_extra={'example': 1})
    title: str = Field(..., max_length=100, json_schema_extra={'example': 'My Activity'})
    description: str = Field(..., max_length=500, json_schema_extra={'example': 'Description of my activity'})
    participants_capacity: int = Field(10, gt=1, lt=100, json_schema_extra={'example': 10})
    public: bool = Field(False, json_schema_extra={'example': False})


class ActivityPublic(Activity):
    participants: list[UserPublic] = Field(default_factory=list, json_schema_extra={'example': []})


class ActivityCreate(BaseModel):
    title: str = Field(..., max_length=100, json_schema_extra={'example': 'My Activity'})
    description: str = Field(..., max_length=500, json_schema_extra={'example': 'Description of my activity'})
    participants_capacity: int = Field(10, gt=1, lt=100, json_schema_extra={'example': 10})
    public: bool = Field(False, json_schema_extra={'example': False})


def _validate_invitation_update(invitation_id: int, current_user_id: int) -> Invitation:
    invitation = services.activity_service.get_invitation_by_id(invitation_id) 
    if not invitation:
        raise HTTPException(status_code=404, detail='Invitation not found')
    elif invitation.target != current_user_id:
        raise HTTPException(status_code=403, detail='User cannot modify this invitation')
    elif invitation.status != InvitationStatus.PENDING:
        raise HTTPException(status_code=400, detail='Only pending invitations can be modified')
    return invitation


@router.post('/create', response_model=ActivityPublic, status_code=201)
async def create_activity(
    form_data: ActivityCreate,
    current_user = Depends(parse_token_and_get_user),
):
    ## TODO: Simple validation to limit the number of activities a user can create. This is just an example, in a real application you might want to implement a more robust solution.
    current_activities = services.activity_service.get_user_activities(current_user.id)
    if len(current_activities) >= 5:
        raise HTTPException(status_code=400, detail='User cannot create more than 5 activities')
    
    return services.activity_service.create({
        **form_data.model_dump(),
        'creator_id': current_user.id
    })


@router.post('/{activity_id}/invite/{user_id}', status_code=201)
async def invite_user(
    activity_id: int,
    user_id: int,
    current_user = Depends(parse_token_and_get_user),
):
    activity = services.activity_service.get_by_id(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail='Activity not found')
    
    creator = activity.creator_id == current_user.id
    if not creator:
        raise HTTPException(status_code=403, detail='Only the creator of the activity can send invitations')

    return services.activity_service.send_invitation(target=user_id, to=activity_id)


@router.get('/my', response_model=list[ActivityPublic])
async def get_my_activities(current_user = Depends(parse_token_and_get_user)):
    return services.activity_service.get_user_activities(current_user.id)


@router.get('/', response_model=list[ActivityPublic])
async def list_activities():
    return services.activity_service.get_public_activities()


@router.get('/{activity_id}', response_model=ActivityPublic)
async def get_activity(activity_id: int):
    activity = services.activity_service.get_activity_with_participants(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail='Activity not found')
    return activity


@router.post('/invitations/{invitation_id}/reject', status_code=200)
async def reject_invitation(
    invitation_id: int,
    current_user = Depends(parse_token_and_get_user),
):
    invitation = _validate_invitation_update(invitation_id, current_user.id)
    services.activity_service.reject_invitation(invitation.id)
    return {'detail': 'Invitation rejected successfully'}
    

@router.post('/invitations/{invitation_id}/accept', status_code=200)
async def accept_invitation(
    invitation_id: int,
    current_user = Depends(parse_token_and_get_user),
):
    invitation = _validate_invitation_update(invitation_id, current_user.id)
    services.activity_service.accept_invitation(invitation.id)
    return {'detail': 'Invitation accepted successfully'}
