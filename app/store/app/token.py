from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

import jwt
from fastapi_jwt_auth import AuthJWT

from core.settings import jwt_settings

if TYPE_CHECKING:
    from schemas import JWT


class TokenAccessor:
    def encode_email_confirmation_token(self, subject: JWT) -> str:
        subject = {"sub": subject.dict()}
        return jwt.encode(
            subject=subject,
            key=jwt_settings.JWT_SECRET_KEY,
            algorithm=jwt_settings.ALGORITHM,
        )

    def decode_email_confirmation_token(self, token: str) -> Dict[str, Any]:
        decoded = jwt.decode(
            token, key=jwt_settings.JWT_SECRET_KEY, algorithms=[jwt_settings.ALGORITHM]
        )
        return decoded.get("sub")

    def create_access_token(self, subject: JWT, authorize: AuthJWT) -> str:
        return authorize.create_access_token(
            subject=subject.json(),
            expires_time=jwt_settings.ACCESS_TOKEN_EXPIRATION_TIME,
        )

    def create_refresh_token(self, subject: JWT, authorize: AuthJWT) -> str:
        return authorize.create_refresh_token(
            subject=subject.json(),
            expires_time=jwt_settings.REFRESH_TOKEN_EXPIRATION_TIME,
        )
