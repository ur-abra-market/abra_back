from corecrud import Options, Where
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body
from fastapi.responses import Response
from sqlalchemy.orm import selectinload
from starlette import status

from core.app import crud
from core.depends import AuthJWT, Authorization, AuthorizationRefresh, DatabaseSession
from core.depends.google_token import verify_google_token
from core.security import check_hashed_password
from enums import UserType
from orm import UserModel
from schemas import ApplicationResponse, BodyLoginRequest, User
from typing_ import RouteReturnT
from utils.cookies import set_and_create_tokens_cookies

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


@router.get(
    path="/role/",
    summary="WORKS: Return a current user role.",
    response_model=ApplicationResponse[UserType],
    status_code=status.HTTP_200_OK,
)
async def get_user_role(user: Authorization) -> RouteReturnT:
    return {
        "ok": True,
        "result": UserType.SUPPLIER if user.is_supplier else UserType.SELLER,
    }


@router.post(
    path="/google_auth",
    summary='WORKS: User google auth (need -H  "Authorization: Bearer <token_id>" in headers)',
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def google_auth(
    response: Response,
    authorize: AuthJWT,
    session: DatabaseSession,
    google_user_info: dict = Depends(verify_google_token),
) -> RouteReturnT:
    user = await crud.users.select.one(
        Where(UserModel.email == google_user_info["email"]),
        session=session,
    )
    if not user or not user.is_verified or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong email, maybe email was not confirmed or account was deleted?",
        )

    set_and_create_tokens_cookies(response=response, authorize=authorize, subject=user.id)

    return {
        "ok": True,
        "result": True,
    }
