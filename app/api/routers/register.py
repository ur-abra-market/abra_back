from fastapi import APIRouter
from fastapi.background import BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path
from fastapi_mail import MessageSchema, MessageType
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.app import crud, fm
from core.depends import AuthJWT, DatabaseSession
from core.security import create_access_token, hash_password
from core.settings import application_settings, fastapi_uvicorn_settings
from enums import UserType
from orm import (
    SellerImageModel,
    SellerModel,
    SupplierModel,
    UserCredentialsModel,
    UserModel,
    UserNotificationModel,
)
from schemas import (
    ApplicationResponse,
    BodyRegisterRequest,
    QueryTokenConfirmationRequest,
)
from typing_ import RouteReturnT

from core.depends import AuthJWT
from .login import set_and_create_tokens_cookies

router = APIRouter()


async def register_user_core(
    request: BodyRegisterRequest, user: UserModel, session: AsyncSession
) -> None:
    await crud.users_credentials.insert.one(
        session=session,
        values={
            UserCredentialsModel.user_id: user.id,
            UserCredentialsModel.password: hash_password(password=request.password),
        },
    )
    if user.is_supplier:
        await crud.suppliers.insert.one(session=session, values={SupplierModel.user_id: user.id})
    else:
        seller = await crud.sellers.insert.one(
            session=session, values={SellerModel.user_id: user.id}
        )
        await crud.sellers_images.insert.one(
            session=session, values={SellerImageModel.seller_id: seller.id}
        )
    await crud.users_notifications.insert.one(
        session=session, values={UserNotificationModel.user_id: user.id}
    )


async def send_confirmation_token(authorize: AuthJWT, user_id: int, email: str) -> None:
    token = create_access_token(subject=user_id, authorize=authorize)

    await fm.send_message(
        message=MessageSchema(
            subject="Email confirmation",
            recipients=[email],
            template_body={
                "url": application_settings.confirm_registration,
                "token": token,
            },
            subtype=MessageType.html,
        ),
        template_name="confirm.html.jinja2",
    )


@router.post(
    path="/{user_type}/",
    summary="WORKS: User registration.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def register_user(
    authorize: AuthJWT,
    session: DatabaseSession,
    background_tasks: BackgroundTasks,
    request: BodyRegisterRequest = Body(...),
    user_type: UserType = Path(...),
) -> RouteReturnT:
    is_verified = fastapi_uvicorn_settings.DEBUG

    user = await crud.users.insert.one(
        session=session,
        values={
            UserModel.email: request.email,
            UserModel.is_supplier: user_type == UserType.SUPPLIER,
            UserModel.is_verified: is_verified,
        },
    )
    await register_user_core(request=request, user=user, session=session)

    background_tasks.add_task(
        send_confirmation_token, authorize=authorize, user_id=user.id, email=request.email
    )

    return {
        "ok": True,
        "result": True,
        "detail": "Please, visit your email to confirm registration",
    }


async def confirm_registration(session: AsyncSession, user_id: int) -> None:
    await crud.users.update.one(
        session=session,
        values={
            UserModel.is_verified: True,
        },
        where=UserModel.id == user_id,
    )


@router.get(
    path="/confirmEmail/",
    summary="WORKS: Processing token that was sent to user during the registration process.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def email_confirmation(
    response: Response,
    authorize: AuthJWT,
    session: DatabaseSession,
    request: QueryTokenConfirmationRequest = Depends(),
) -> RouteReturnT:
    try:
        user_id = authorize.get_raw_jwt(encoded_token=request.token)["sub"]
    except Exception:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    user = await crud.users.get.one(
        session=session,
        where=[UserModel.id == user_id],
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user:
        set_and_create_tokens_cookies(response=response, authorize=authorize, subject=user.id)
        RedirectResponse("/")

    await confirm_registration(session=session, user_id=user.id)

    return {
        "ok": True,
        "result": True,
    }
