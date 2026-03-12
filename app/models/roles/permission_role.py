from sqlmodel import Field, SQLModel


class PermissionRole(SQLModel, table=True):
    __tablename__ = 'permission_roles'

    role_id: int | None = Field(default=None, foreign_key='role.id', primary_key=True)
    permission_id: int | None = Field(default=None, foreign_key='permission.id', primary_key=True)
