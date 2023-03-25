from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.depends import get_session
from core.settings import application_settings
from core.tools import store
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
    ApplicationResponse,
    BodyRegisterRequest,
    QueryTokenConfirmationRequest,
    JWT,
)

router = APIRouter()


async def register_user_core(
    request: BodyRegisterRequest, user: UserModel, session: AsyncSession
) -> None:
    await store.orm.users_credentials.insert_one(
        session=session,
        values={
            UserCredentialsModel.user_id: user.id,
            UserCredentialsModel.password: store.app.pwd.hash_password(password=request.password),
        },
    )
    if user.is_supplier:
        supplier = await store.orm.suppliers.insert_one(
            session=session, values={SupplierModel.user_id: user.id}
        )
        await store.orm.companies.insert_one(
            session=session, values={CompanyModel.supplier_id: supplier.id}
        )
    else:
        seller = await store.orm.sellers.insert_one(
            session=session, values={SellerModel.user_id: user.id}
        )
        await store.orm.orders.insert_one(
            session=session, values={OrderModel.seller_id: seller.id}
        )
    await store.orm.users_notifications.insert_one(
        session=session, values={UserNotificationModel.user_id: user.id}
    )


async def send_confirmation_token(user_id: int, email: str) -> None:
    token = store.app.token.encode_email_confirmation_token(subject=JWT(user_id=user_id))
    await store.mail.send_confirmation_mail(
        subject="Email confirmation",
        recipients=email,
        host=application_settings.APP_URL,
        token=token,
    )


@router.post(
    path="/{user_type}",
    summary="WORKS: User registration.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def register_user(
    request: BodyRegisterRequest = Body(...),
    user_type: UserType = Path(...),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    exists = await store.orm.users.get_one(
        session=session, where=[UserModel.email == request.email]
    )
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with current email already registered",
        )

    user = await store.orm.users.insert_one(
        session=session,
        values={
            UserModel.email: request.email,
            UserModel.is_supplier: user_type == UserType.SUPPLIER,
        },
    )
    await register_user_core(request=request, user=user, session=session)

    await send_confirmation_token(user_id=user.id, email=request.email)

    return {
        "ok": True,
        "result": True,
        "detail": "Please visit your email to confirm registration",
    }


async def confirm_registration(session: AsyncSession, user_id: int) -> None:
    await store.orm.users.update_one(
        session=session,
        values={
            UserModel.is_verified: True,
        },
        where=UserModel.id == user_id,
    )


@router.get(
    path="/emailConfirmationResult",
    summary="WORKS: Processing token that was sent to user during the registration process.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/email_confirmation_result",
    deprecated=True,
    summary="WORKS: Processing token that was sent to user during the registration process.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def email_confirmation(
    request: QueryTokenConfirmationRequest = Depends(),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    try:
        jwt = JWT.parse_obj(store.app.token.decode_email_confirmation_token(token=request.token))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    user = await store.orm.users.get_one(session=session, where=[UserModel.id == jwt.user_id])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await confirm_registration(session=session, user_id=user.id)

    return {
        "ok": True,
        "result": True,
    }
