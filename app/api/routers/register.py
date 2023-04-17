# mypy: disable-error-code="arg-type,return-value"

from fastapi import APIRouter
from fastapi.background import BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path
from fastapi_jwt_auth import AuthJWT
from fastapi_mail import MessageSchema, MessageType
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.depends import get_session
from core.mail import fm
from core.orm import orm
from core.security import create_access_token, hash_password
from core.settings import application_settings, fastapi_settings
from enums import UserType
from orm import (
    OrderModel,
    SellerImageModel,
    SellerModel,
    SupplierModel,
    UserCredentialsModel,
    UserModel,
    UserNotificationModel,
)
from schemas import (
    JWT,
    ApplicationResponse,
    BodyRegisterRequest,
    QueryTokenConfirmationRequest,
)

router = APIRouter()


async def register_user_core(
    request: BodyRegisterRequest, user: UserModel, session: AsyncSession
) -> None:
    await orm.users_credentials.insert_one(
        session=session,
        values={
            UserCredentialsModel.user_id: user.id,
            UserCredentialsModel.password: hash_password(password=request.password),
        },
    )
    if user.is_supplier:
        await orm.suppliers.insert_one(session=session, values={SupplierModel.user_id: user.id})
    else:
        seller = await orm.sellers.insert_one(
            session=session, values={SellerModel.user_id: user.id}
        )
        await orm.orders.insert_one(session=session, values={OrderModel.seller_id: seller.id})
        await orm.sellers_images.insert_one(
            session=session, values={SellerImageModel.seller_id: seller.id}
        )
    await orm.users_notifications.insert_one(
        session=session, values={UserNotificationModel.user_id: user.id}
    )


async def send_confirmation_token(authorize: AuthJWT, user_id: int, email: str) -> None:
    token = create_access_token(subject=JWT(user_id=user_id), authorize=authorize)

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
    background_tasks: BackgroundTasks,
    request: BodyRegisterRequest = Body(...),
    user_type: UserType = Path(...),
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    if await orm.users.get_one_by(session=session, email=request.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Try another email")

    is_verified = fastapi_settings.DEBUG

    user = await orm.users.insert_one(
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
    await orm.users.update_one(
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
@router.get(
    path="/email_confirmation_result/",
    description="Moved to /register/confirmEmail",
    deprecated=True,
    summary="WORKS: Processing token that was sent to user during the registration process.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
@router.get(
    path="register/email-confirmation/",
    description="Moved to /register/confirmEmail",
    deprecated=True,
    summary="WORKS: Processing token that was sent to user during the registration process.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def email_confirmation(
    request: QueryTokenConfirmationRequest = Depends(),
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    try:
        jwt = JWT.parse_raw(authorize.get_raw_jwt(encoded_token=request.token)["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    user = await orm.users.get_one_by(session=session, id=jwt.user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await confirm_registration(session=session, user_id=user.id)

    return {
        "ok": True,
        "result": True,
    }
