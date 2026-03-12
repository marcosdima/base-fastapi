from sqlmodel import Field, SQLModel


class UserRole(SQLModel, table=True):
    __tablename__ = 'user_roles'

    user_id: int | None = Field(default=None, foreign_key='user.id', primary_key=True)
    role_id: int | None = Field(default=None, foreign_key='role.id', nullable=False, index=True)
