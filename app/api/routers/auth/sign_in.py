from corecrud import Options, Where
from fastapi import APIRouter, Depends
from fastapi.param_functions import Body
from fastapi.responses import Response
from sqlalchemy.orm import selectinload
from starlette import status

from core import exceptions
from core.app import crud
from core.depends import AuthJWT, AuthorizationRefresh, DatabaseSession
from core.depends.google_token import google_verifier
from core.security import check_hashed_password
from orm import UserModel
from schemas import ApplicationResponse
from schemas.uploads import LoginUpload
from typing_ import DictStrAny, RouteReturnT
from utils.cookies import set_and_create_tokens_cookies

router = APIRouter()


@router.post(
    path="/",
    summary="WORKS: User login (token creation).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def sign_in(
    response: Response,
    authorize: AuthJWT,
    session: DatabaseSession,
    request: LoginUpload = Body(...),
) -> RouteReturnT:
    user = await crud.users.select.one(
        Where(UserModel.email == request.email),
        Options(selectinload(UserModel.credentials)),
        session=session,
    )
    if (
        not user  # user not found
        or not check_hashed_password(
            password=request.password, hashed=user.credentials.password
        )  # password doesn't  matches
        or not user.is_verified  # user doesn't verify their email
        or user.is_deleted  # account was deleted
    ):
        raise exceptions.ForbiddenException(
            detail="Wrong email or password, maybe email was not confirmed or account was deleted?",
        )

    set_and_create_tokens_cookies(response=response, authorize=authorize, subject=user.id)

    return {
        "ok": True,
        "result": True,
    }


@router.post(
    path="/refresh",
    summary="WORKS (need X-CSRF-TOKEN in headers): Refresh all tokens.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def refresh_jwt_tokens(
    response: Response,
    authorize: AuthJWT,
    user: AuthorizationRefresh,
) -> RouteReturnT:
    set_and_create_tokens_cookies(response=response, authorize=authorize, subject=user.id)

    return {
        "ok": True,
        "result": True,
    }


@router.post(
    path="/googleAuth",
    summary="WORKS: User google auth",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def google_sign_in(
    response: Response,
    authorize: AuthJWT,
    session: DatabaseSession,
    google_user_info: DictStrAny = Depends(google_verifier.verify_google_token),
) -> RouteReturnT:
    user = await crud.users.select.one(
        Where(UserModel.email == google_user_info["email"]),
        session=session,
    )
    if not user or not user.is_verified or user.is_deleted:
        raise exceptions.ForbiddenException(
            detail="Wrong email or password, maybe email was not confirmed or account was deleted?",
        )

    set_and_create_tokens_cookies(response=response, authorize=authorize, subject=user.id)

    return {
        "ok": True,
        "result": True,
    }
