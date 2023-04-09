from __future__ import annotations

from typing import TYPE_CHECKING, cast

from fastapi_jwt_auth import AuthJWT

from core.settings import jwt_settings

if TYPE_CHECKING:
    from schemas import JWT


def create_access_token(subject: JWT, authorize: AuthJWT) -> str:
    return cast(
        str,
        authorize.create_access_token(
            subject=subject.json(),
            expires_time=jwt_settings.ACCESS_TOKEN_EXPIRATION_TIME,
        ),
    )


def create_refresh_token(subject: JWT, authorize: AuthJWT) -> str:
    return cast(
        str,
        authorize.create_refresh_token(
            subject=subject.json(),
            expires_time=jwt_settings.REFRESH_TOKEN_EXPIRATION_TIME,
        ),
    )
