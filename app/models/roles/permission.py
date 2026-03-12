from sqlmodel import Field
from ..base_model import BaseModel


class Permission(BaseModel, table=True):
    name: str = Field(unique=True, index=True, min_length=3, max_length=25)
    description: str = Field(max_length=200)
