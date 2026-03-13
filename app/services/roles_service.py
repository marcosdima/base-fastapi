from .base_service import BaseService
from ..models import Permission, PermissionRole, Role, UserRole
from ..utils import PermissionName
from pwdlib import PasswordHash
from sqlmodel import select


password_hash = PasswordHash.recommended()


class RoleService(BaseService):
    def __init__(self, session):
        super().__init__(model=Role, session=session)


    def user_has_role(self, user_id: int) -> bool:
        has = select(UserRole).where(UserRole.user_id == user_id)
        return self.session.exec(has).first() is not None
    

    def assign_role_to_user(self, user_id: int, new_role_id: int):
        user_role = select(UserRole).where(UserRole.user_id == user_id)
        existing_user_role = self.session.exec(user_role).first()

        if existing_user_role:
            existing_user_role.role_id = new_role_id
            self.session.add(existing_user_role)
        else:
            new_user_role = UserRole(user_id=user_id, role_id=new_role_id)
            self.session.add(new_user_role)

        self.session.commit()


    def remove_role_from_user(self, user_id: int) -> bool:
        user_role = select(UserRole).where(UserRole.user_id == user_id)
        existing_user_role = self.session.exec(user_role).first()
        if not existing_user_role:
            return False

        self.session.delete(existing_user_role)
        self.session.commit()
        return True
    

    def validate_permissions(
            self,
            user_id: int,
            permission_required: PermissionName
    ) -> bool:
        query = (
            select(Permission)
                .join(PermissionRole, Permission.id == PermissionRole.permission_id)
                .join(Role, Role.id == PermissionRole.role_id)
                .join(UserRole, Role.id == UserRole.role_id)
                .where(UserRole.user_id == user_id)
                .where(Permission.name == permission_required.value)
        )
        permission = self.session.exec(query).first()
        return permission is not None
