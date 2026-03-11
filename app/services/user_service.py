from .base_service import BaseService
from ..models import User
from pwdlib import PasswordHash
from sqlmodel import select


password_hash = PasswordHash.recommended()


class UserService(BaseService):
    def __init__(self, session):
        super().__init__(model=User, session=session)


    def hash_password(self, password: str) -> str:
        return password_hash.hash(password)


    def verify_password(self, password: str, password_hash_value: str) -> bool:
        return password_hash.verify(password, password_hash_value)


    def get_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()
    

    def create(self, username: str, password: str) -> User:
        hashed_password = self.hash_password(password)
        user = super().create({
            'username': username,
            'password_hash': hashed_password
        })
        return user