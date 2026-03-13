from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from .dependencies.auth import parse_token_and_get_user
from .. import services
from ..utils import PermissionName

router = APIRouter()


class AssignRoleIn(BaseModel):
    role_id: int = Field(1, ge=1, json_schema_extra={'example': 1})


class AssignRoleOut(BaseModel):
    user_id: int = Field(..., json_schema_extra={'example': 1})
    role_id: int = Field(..., json_schema_extra={'example': 1})


class RemoveRoleOut(BaseModel):
    detail: str = Field(..., json_schema_extra={'example': 'Role removed successfully'})


@router.post('/{user_id}/assign', response_model=AssignRoleOut, status_code=201)
async def assign_role(
    form_data: AssignRoleIn,
    user_id: int = Path(..., ge=1, json_schema_extra={'example': 1}),
    current_user: object = Depends(parse_token_and_get_user),
):
    if services.roles_service.validate_permissions(
        user_id=current_user.id,
        permission_required=PermissionName.ASSIGN_ROLES,
    ) is False:
        raise HTTPException(
            status_code=403,
            detail='You do not have permission to assign roles',
        )


    user = services.user_service.get_by_id(user_id)
    if not user or user.disabled:
        raise HTTPException(status_code=404, detail='User not found')

    role = services.roles_service.get_by_id(form_data.role_id)
    if not role or role.disabled:
        raise HTTPException(status_code=404, detail='Role not found')

    services.roles_service.assign_role_to_user(user_id, role.id)

    return {
        'user_id': user_id,
        'role_id': role.id,
    }


@router.delete('/{user_id}/remove', status_code=200, response_model=RemoveRoleOut)
async def remove_role(
    user_id: int = Path(..., ge=1, json_schema_extra={'example': 1}),
    current_user: object = Depends(parse_token_and_get_user),
):
    if services.roles_service.validate_permissions(
        user_id=current_user.id,
        permission_required=PermissionName.REMOVE_USER_ROLE,
    ) is False:
        raise HTTPException(
            status_code=403,
            detail='You do not have permission to remove roles',
        )
    
    removed = services.roles_service.remove_role_from_user(user_id)
    if not removed:
        raise HTTPException(status_code=404, detail='Role assignment not found')

    return {'detail': 'Role removed successfully'}


@router.get('/', response_model=list[str])
async def list_roles(current_user: object = Depends(parse_token_and_get_user)):
    if services.roles_service.validate_permissions(
        user_id=current_user.id,
        permission_required=PermissionName.GET_ROLES,
    ) is False:
        raise HTTPException(
            status_code=403,
            detail='You do not have permission to view roles',
        )

    roles = services.roles_service.get_all()
    return [role.name for role in roles]