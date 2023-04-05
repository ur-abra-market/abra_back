from fastapi import APIRouter
from fastapi.background import BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.depends import get_session
from core.security import hash_password
from core.settings import application_settings
from core.tools import tools
from enums import UserType
from orm import (
    CompanyModel,
    OrderModel,
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
    await tools.store.orm.users_credentials.insert_one(
        session=session,
        values={
            UserCredentialsModel.user_id: user.id,
            UserCredentialsModel.password: hash_password(password=request.password),
        },
    )
    if user.is_supplier:
        supplier = await tools.store.orm.suppliers.insert_one(
            session=session, values={SupplierModel.user_id: user.id}
        )
        await tools.store.orm.companies.insert_one(
            session=session, values={CompanyModel.supplier_id: supplier.id}
        )
    else:
        seller = await tools.store.orm.sellers.insert_one(
            session=session, values={SellerModel.user_id: user.id}
        )
        await tools.store.orm.orders.insert_one(
            session=session, values={OrderModel.seller_id: seller.id}
        )
    await tools.store.orm.users_notifications.insert_one(
        session=session, values={UserNotificationModel.user_id: user.id}
    )


async def send_confirmation_token(authorize: AuthJWT, user_id: int, email: str) -> None:
    token = tools.store.app.token.create_access_token(
        subject=JWT(user_id=user_id),
        authorize=authorize,
    )
    await tools.store.mail.confirm.send(
        subject="Email confirmation",
        recipients=email,
        host=application_settings.APP_URL,
        token=token,
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
    exists = await tools.store.orm.users.get_one(
        session=session, where=[UserModel.email == request.email]
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with current email already registered",
        )

    user = await tools.store.orm.users.insert_one(
        session=session,
        values={
            UserModel.email: request.email,
            UserModel.is_supplier: user_type == UserType.SUPPLIER,
        },
    )
    await register_user_core(request=request, user=user, session=session)

    background_tasks.add_task(
        send_confirmation_token, authorize=authorize, user_id=user.id, email=request.email
    )

    return {
        "ok": True,
        "result": True,
        "detail": "Please visit your email to confirm registration",
    }


async def confirm_registration(session: AsyncSession, user_id: int) -> None:
    await tools.store.orm.users.update_one(
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

    user = await tools.store.orm.users.get_one(
        session=session, where=[UserModel.id == jwt.user_id]
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await confirm_registration(session=session, user_id=user.id)

    return {
        "ok": True,
        "result": True,
    }
