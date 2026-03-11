from sqlmodel import Field
from .base_model import BaseModel

class User(BaseModel, table=True):
    username: str = Field(index=True, min_length=3, max_length=25)
    password_hash: str = Field(min_length=60, max_length=160)
