from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from .. import services
from .dependencies.auth import create_access_token


router = APIRouter()


class User(BaseModel):
    username: str = Field(..., json_schema_extra={'example': 'john_doe'})


class UserIn(User):
    password: str = Field(
        ..., min_length=8, json_schema_extra={'example': 'Secure@123'}
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '@$!%*?&' for c in v):
            raise ValueError('Password must contain at least one special character (@$!%*?&)')
        return v


class UserOut(User):
    id: int = Field(..., json_schema_extra={'example': 1})
    token: str = Field(..., json_schema_extra={'example': 'jwt_token_example'})


def _build_user_out(user) -> dict:
    return {
        'id': user.id,
        'username': user.username,
        'token': create_access_token(user_id=user.id, username=user.username),
    }
    

@router.post('/signin', response_model=UserOut, status_code=201)
async def signin(form_data: UserIn):
    try:
        user = services.user_service.create(
            password=form_data.password,
            username=form_data.username
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _build_user_out(user)


@router.post('/login', response_model=UserOut)
async def login(form_data: UserIn):
    user = services.user_service.get_by_username(form_data.username)
    if not user:
        raise HTTPException(status_code=404, detail='Username not found')
    elif not services.user_service.verify_password(
        form_data.password,
        user.password_hash,
    ):
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return _build_user_out(user)


@router.get('/users', response_model=list[UserOut])
async def get_users():
    return services.user_service.get_all()