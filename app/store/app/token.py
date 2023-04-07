from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi_jwt_auth import AuthJWT

from core.settings import jwt_settings

if TYPE_CHECKING:
    from schemas import JWT


class TokenAccessor:
    @staticmethod
    def create_access_token(subject: JWT, authorize: AuthJWT) -> str:
        return authorize.create_access_token(  # type: ignore
            subject=subject.json(),
            expires_time=jwt_settings.ACCESS_TOKEN_EXPIRATION_TIME,
        )

    @staticmethod
    def create_refresh_token(subject: JWT, authorize: AuthJWT) -> str:
        return authorize.create_refresh_token(  # type: ignore
            subject=subject.json(),
            expires_time=jwt_settings.REFRESH_TOKEN_EXPIRATION_TIME,
        )
