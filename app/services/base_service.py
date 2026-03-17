from typing import Any, Generic, TypeVar

from sqlmodel import Session, select
from ..models import BaseModel


ModelType = TypeVar('ModelType', bound=BaseModel)


class BaseService(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: Session):
        self.model = model
        self.session = session


    def get_all(self, include_disabled: bool = False) -> list[ModelType]:
        stmt = select(self.model)
        if not include_disabled:
            stmt = stmt.where(self.model.disabled == False)
        return self.session.exec(stmt).all()


    def get_by_id(self, id: int) -> ModelType | None:
        return self.session.get(self.model, id)
    

    def create(self, obj_in: Any) -> ModelType:
        obj = self.model.model_validate(obj_in)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj
    

    def remove(self, id: int, soft: bool = True):
        obj = self.get_by_id(id)
        if obj:
            if soft:
                obj.disabled = True
                self.session.add(obj)
            else:
                self.session.delete(obj)
            self.session.commit()
            return True
        return False
    

    def update(self, id: int, obj_in: Any) -> ModelType | None:
        obj = self.get_by_id(id)
        if obj:
            obj_data = obj.model_dump()
            update_data = (
                obj_in.model_dump(exclude_unset=True)
                if hasattr(obj_in, 'model_dump')
                else obj_in
            )
            for field in obj_data:
                if field in update_data:
                    setattr(obj, field, update_data[field])
            self.session.add(obj)
            self.session.commit()
            self.session.refresh(obj)
            return obj
        return None