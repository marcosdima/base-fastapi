from sqlmodel import Field
from ..base_model import BaseModel


class Participate(BaseModel, table=True):
    to: int = Field(foreign_key="activity.id")
    participant: int = Field(foreign_key="user.id")