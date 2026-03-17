from enum import StrEnum
from sqlmodel import Field
from ..base_model import BaseModel


class InvitationStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class Invitation(BaseModel, table=True):
    to: int = Field(foreign_key="activity.id")
    target: int = Field(foreign_key="user.id")
    status: InvitationStatus = Field(default=InvitationStatus.PENDING)
