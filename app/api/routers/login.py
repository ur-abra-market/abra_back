from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends
from fastapi.responses import Response
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.app import crud
from core.depends import (
    UserObjects,
    auth_refresh_token_required,
    auth_required,
    get_session,
)
from core.security import (
    check_hashed_password,
    create_access_token,
    create_refresh_token,
)
from core.settings import jwt_settings
from orm import UserModel
from schemas import JWT, ApplicationResponse, BodyLoginRequest, User
from typing_ import RouteReturnT

router = APIRouter()


def set_and_create_tokens_cookies(response: Response, authorize: AuthJWT, subject: JWT) -> None:
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


@router.post(
    path="/",
    summary="WORKS: User login (token creation).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def login_user(
    response: Response,
    request: BodyLoginRequest = Body(...),
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    user = await crud.users.get.one(
        session=session,
        where=[UserModel.email == request.email],
        options=[selectinload(UserModel.credentials)],
    )
    if (
        not user  # user not found
        or not check_hashed_password(
            password=request.password, hashed=user.credentials.password
        )  # password doesn't  matches
        or not user.is_verified  # user doesn't verify their email
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong email or password, maybe email not confirmed?",
        )

    subject = JWT(user_id=user.id)
    set_and_create_tokens_cookies(response=response, authorize=authorize, subject=subject)

    return {
        "ok": True,
        "result": True,
    }


@router.post(
    path="/refresh/",
    summary="WORKS (need X-CSRF-TOKEN in headers): Refresh all tokens.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def refresh_jwt_tokens(
    response: Response,
    authorize: AuthJWT = Depends(),
    user: UserObjects = Depends(auth_refresh_token_required),
) -> RouteReturnT:
    subject = JWT(user_id=user.schema.id)
    set_and_create_tokens_cookies(response=response, authorize=authorize, subject=subject)

    return {
        "ok": True,
        "result": True,
    }


@router.get(
    path="/current/",
    summary="WORKS: Return a current user.",
    response_model=ApplicationResponse[User],
    status_code=status.HTTP_200_OK,
)
async def current(user: UserObjects = Depends(auth_required)) -> RouteReturnT:
    if user.orm.supplier:
        return {
            "ok": True,
            "result": user.schema,
            "detail": {
                "has_profile": bool(user.orm.supplier.company),
            },
        }

    return {
        "ok": True,
        "result": user.schema,
    }
