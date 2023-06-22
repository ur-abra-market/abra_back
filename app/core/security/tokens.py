from __future__ import annotations

from typing import Union, cast

from fastapi_jwt_auth import AuthJWT

from core.settings import jwt_settings


def create_access_token(subject: Union[int, str], authorize: AuthJWT) -> str:
    return cast(
        str,
        authorize.create_access_token(
            subject=subject,
            expires_time=jwt_settings.ACCESS_TOKEN_EXPIRATION_TIME,
        ),
    )


def create_refresh_token(subject: Union[int, str], authorize: AuthJWT) -> str:
    return cast(
        str,
        authorize.create_refresh_token(
            subject=subject,
            expires_time=jwt_settings.REFRESH_TOKEN_EXPIRATION_TIME,
        ),
    )
