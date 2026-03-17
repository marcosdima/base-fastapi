from sqlmodel import Field
from ..base_model import BaseModel


class Activity(BaseModel, table=True):
    creator_id: int = Field(foreign_key="user.id")
    title: str = Field(max_length=100)
    description: str = Field(max_length=500)
    participants_capacity: int = Field(default=10, gt=1, lt=100)
    public: bool = Field(default=False)

