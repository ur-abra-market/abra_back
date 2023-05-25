from corecrud import Options, Where
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import selectinload
from starlette import status

from core.app import crud
from core.depends import AuthJWT, Authorization, AuthorizationRefresh, DatabaseSession
from core.security import check_hashed_password
from orm import UserModel
from schemas import ApplicationResponse, BodyLoginRequest, User
from typing_ import RouteReturnT
from utils.cookies import set_and_create_tokens_cookies
from utils.fastapi import Body

router = APIRouter()


@router.post(
    path="/",
    summary="WORKS: User login (token creation).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def login_user(
    response: Response,
    authorize: AuthJWT,
    session: DatabaseSession,
    request: BodyLoginRequest = Body(...),
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
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong email or password, maybe email was not confirmed or account was deleted?",
        )

    set_and_create_tokens_cookies(response=response, authorize=authorize, subject=user.id)

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
    authorize: AuthJWT,
    user: AuthorizationRefresh,
) -> RouteReturnT:
    set_and_create_tokens_cookies(response=response, authorize=authorize, subject=user.id)

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
async def current(user: Authorization) -> RouteReturnT:
    if user.supplier:
        return {
            "ok": True,
            "result": user,
            "detail": {
                "has_profile": bool(user.supplier.company),
            },
        }

    return {
        "ok": True,
        "result": user,
    }
