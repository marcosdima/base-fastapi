from sqlmodel import Field, SQLModel


class BaseModel(SQLModel, table=False):
    id: int | None = Field(default=None, primary_key=True)
