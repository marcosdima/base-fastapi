from sqlmodel import Session, select

class BaseService:
    def __init__(self, model: type, session: Session):
        self.model = model
        self.session = session


    def get_all(self):
        return self.session.exec(select(self.model)).all()
    

    def get_by_id(self, id: int):
        return self.session.get(self.model, id)
    

    def create(self, obj_in):
        obj = self.model.model_validate(obj_in)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj