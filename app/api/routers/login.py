from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends
from fastapi.responses import JSONResponse, Response
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.depends import UserObjects, auth_required, get_session, refresh_token_required
from core.settings import jwt_settings
from core.tools import store
from orm import UserModel
from schemas import JWT, ApplicationResponse, BodyLoginRequest, User

router = APIRouter()


def set_and_create_tokens_cookies(response: Response, authorize: AuthJWT, subject: JWT) -> None:
    access_token, refresh_token = (
        store.app.token.create_access_token(subject=subject, authorize=authorize),
        store.app.token.create_refresh_token(subject=subject, authorize=authorize),
    )

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
    response: JSONResponse,
    request: BodyLoginRequest = Body(...),
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    user = await store.orm.users.get_one(
        session=session,
        options=[selectinload(UserModel.credentials)],
        where=[UserModel.email == request.email],
    )
    if (
        not user
        or not store.app.pwd.check_hashed_password(
            password=request.password, hashed=user.credentials.password
        )
        or not user.is_verified
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
    path="/refresh",
    summary="WORKS (need X-CSRF-TOKEN in headers): Refresh all tokens.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def refresh_jwt_tokens(
    response: JSONResponse,
    authorize: AuthJWT = Depends(),
    subject: JWT = Depends(refresh_token_required),
) -> ApplicationResponse[bool]:
    set_and_create_tokens_cookies(response=response, authorize=authorize, subject=subject)

    return {
        "ok": True,
        "result": True,
    }


@router.get(
    path="/current",
    summary="WORKS: Return a current user.",
    response_model=ApplicationResponse[User],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/check_auth",
    description="Moved to /login/current",
    deprecated=True,
    summary="WORKS: Return a current user.",
    response_model=ApplicationResponse[User],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def current(user: UserObjects = Depends(auth_required)) -> ApplicationResponse[User]:
    return {
        "ok": True,
        "result": user.schema,
    }
