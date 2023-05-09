from typing import Union

from fastapi.responses import Response
from fastapi_jwt_auth import AuthJWT

from core.security import create_access_token, create_refresh_token
from core.settings import jwt_settings


def unset_jwt_cookies(response: Response, authorize: AuthJWT) -> None:
    authorize.unset_jwt_cookies(response=response)


def set_and_create_tokens_cookies(
    response: Response, authorize: AuthJWT, subject: Union[int, str]
) -> None:
    access_token, refresh_token = (
        create_access_token(subject=subject, authorize=authorize),
        create_refresh_token(subject=subject, authorize=authorize),
    )

    response.headers["access-control-expose-headers"] = "Set-Cookie"

    authorize.set_access_cookies(
        response=response,
        encoded_access_token=access_token,
        max_age=jwt_settings.ACCESS_TOKEN_EXPIRATION_TIME,
    )
    authorize.set_refresh_cookies(
        response=response,
        encoded_refresh_token=refresh_token,
        max_age=jwt_settings.REFRESH_TOKEN_EXPIRATION_TIME,
    )
