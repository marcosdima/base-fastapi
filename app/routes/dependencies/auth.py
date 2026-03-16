from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ... import services
from ...utils.settings import settings


security = HTTPBearer(auto_error=False)


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')


def _b64url_decode(data: str) -> bytes:
    padding = '=' * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(f'{data}{padding}'.encode('utf-8'))


def create_access_token(
    user_id: int,
    username: str,
    expires_delta: timedelta | None = None,
) -> str:
    expire_delta = expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire_at = datetime.now(timezone.utc) + expire_delta

    header = {'alg': 'HS256', 'typ': 'JWT'}
    payload = {
        'sub': str(user_id),
        'username': username,
        'exp': int(expire_at.timestamp()),
    }

    encoded_header = _b64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    encoded_payload = _b64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    signature_input = f'{encoded_header}.{encoded_payload}'.encode('utf-8')
    signature = hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        signature_input,
        hashlib.sha256,
    ).digest()
    encoded_signature = _b64url_encode(signature)

    return f'{encoded_header}.{encoded_payload}.{encoded_signature}'


def verify_token(token: str) -> dict:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid or expired token',
    )

    try:
        encoded_header, encoded_payload, encoded_signature = token.split('.')
    except ValueError as exc:
        raise unauthorized from exc

    signature_input = f'{encoded_header}.{encoded_payload}'.encode('utf-8')
    expected_signature = hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        signature_input,
        hashlib.sha256,
    ).digest()
    try:
        provided_signature = _b64url_decode(encoded_signature)
    except ValueError as exc:
        raise unauthorized from exc

    if not hmac.compare_digest(provided_signature, expected_signature):
        raise unauthorized

    try:
        payload = json.loads(_b64url_decode(encoded_payload).decode('utf-8'))
    except (json.JSONDecodeError, ValueError) as exc:
        raise unauthorized from exc

    exp = payload.get('exp')
    if not isinstance(exp, int):
        raise unauthorized

    now_timestamp = int(datetime.now(timezone.utc).timestamp())
    if exp <= now_timestamp:
        raise unauthorized

    return payload


def parse_token_and_get_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
):
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
        )

    payload = verify_token(credentials.credentials)
    sub = payload.get('sub')
    if not sub or not str(sub).isdigit():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token subject',
        )

    user = services.user_service.get_by_id(int(sub))
    if not user or user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found for token',
        )

    return user
