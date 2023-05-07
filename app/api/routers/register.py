from corecrud import Returning, Values, Where
from fastapi import APIRouter
from fastapi.background import BackgroundTasks
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path
from fastapi.responses import Response
from fastapi_mail import MessageSchema, MessageType
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.app import crud, fm
from core.depends import AuthJWT, Authorization, DatabaseSession, SupplierAuthorization
from core.security import create_access_token, hash_password
from core.settings import application_settings, fastapi_uvicorn_settings
from enums import UserType
from orm import (
    CompanyModel,
    SellerImageModel,
    SellerModel,
    SupplierModel,
    UserCredentialsModel,
    UserModel,
    UserNotificationModel,
)
from schemas import (
    ApplicationResponse,
    BodyCompanyDataRequest,
    BodyRegisterRequest,
    BodySupplierDataRequest,
    BodyUserDataRequest,
    QueryTokenConfirmationRequest,
)
from typing_ import RouteReturnT

from .login import set_and_create_tokens_cookies

router = APIRouter()


async def register_user_core(
    request: BodyRegisterRequest, user: UserModel, session: AsyncSession
) -> None:
    await crud.users_credentials.insert.one(
        Values(
            {
                UserCredentialsModel.user_id: user.id,
                UserCredentialsModel.password: hash_password(password=request.password),
            }
        ),
        Returning(UserCredentialsModel.id),
        session=session,
    )
    if user.is_supplier:
        await crud.suppliers.insert.one(
            Values({SupplierModel.user_id: user.id}),
            Returning(SupplierModel.id),
            session=session,
        )
    else:
        seller = await crud.sellers.insert.one(
            Values({SellerModel.user_id: user.id}),
            Returning(SellerModel.id),
            session=session,
        )
        await crud.sellers_images.insert.one(
            Values(
                {SellerImageModel.seller_id: seller.id},
            ),
            Returning(SellerImageModel.id),
            session=session,
        )
    await crud.users_notifications.insert.one(
        Values({UserNotificationModel.user_id: user.id}),
        Returning(UserNotificationModel.id),
        session=session,
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
        Values(
            {
                UserModel.email: request.email,
                UserModel.is_supplier: user_type == UserType.SUPPLIER,
                UserModel.is_verified: is_verified,
            }
        ),
        Returning(UserModel),
        session=session,
    )
    await register_user_core(request=request, user=user, session=session)

    background_tasks.add_task(
        send_confirmation_token, authorize=authorize, user_id=user.id, email=request.email
    )

    return {
        "ok": True,
        "result": True,
        "detail": {
            "message": "Please, visit your email to confirm registration",
        },
    }


async def confirm_registration(session: AsyncSession, user_id: int) -> None:
    await crud.users.update.one(
        Values(
            {
                UserModel.is_verified: True,
            }
        ),
        Where(UserModel.id == user_id),
        Returning(UserModel.id),
        session=session,
    )


@router.get(
    path="/confirmEmail/",
    summary="WORKS: Processing token that was sent to user during the registration process.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def email_confirmation(
    response: Response,
    session: DatabaseSession,
    authorize: AuthJWT,
    request: QueryTokenConfirmationRequest = Depends(),
) -> RouteReturnT:
    try:
        user_id = authorize.get_raw_jwt(encoded_token=request.token)["sub"]
    except Exception:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")

    user = await crud.users.select.one(
        Where(UserModel.id == user_id),
        session=session,
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    set_and_create_tokens_cookies(response=response, authorize=authorize, subject=user.id)
    await confirm_registration(session=session, user_id=user.id)

    return {
        "ok": True,
        "result": True,
    }


async def send_account_info_core(
    session: AsyncSession,
    user_id: int,
    request: BodyUserDataRequest,
) -> None:
    await crud.users.update.one(
        Values(request.dict()),
        Where(UserModel.id == user_id),
        Returning(UserModel.id),
        session=session,
    )


@router.post(
    path="/account/sendInfo/",
    summary="WORKS: update UserModel with additional information (as part of the first step) such as: first_name, last_name, country_code, phone_number",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def send_account_info(
    user: Authorization,
    session: DatabaseSession,
    request: BodyUserDataRequest = Body(...),
) -> RouteReturnT:
    await send_account_info_core(session=session, user_id=user.id, request=request)

    return {
        "ok": True,
        "result": True,
    }


async def send_business_info_core(
    session: AsyncSession,
    supplier_id: int,
    supplier_data_request: BodySupplierDataRequest,
    company_data_request: BodyCompanyDataRequest,
) -> None:
    await crud.suppliers.update.one(
        Values(supplier_data_request.dict()),
        Where(SupplierModel.id == supplier_id),
        Returning(SupplierModel.id),
        session=session,
    )

    await crud.companies.insert.one(
        Values(
            {
                CompanyModel.supplier_id: supplier_id,
            }
            | company_data_request.dict(),
        ),
        Returning(CompanyModel.id),
        session=session,
    )


@router.post(
    path="/business/sendInfo/",
    summary="WORKS: update SuplierModel with licence information & creates CompanyModel",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def insert_business_info(
    user: SupplierAuthorization,
    session: DatabaseSession,
    supplier_data_request: BodySupplierDataRequest = Body(...),
    company_data_request: BodyCompanyDataRequest = Body(...),
) -> RouteReturnT:
    await send_business_info_core(
        session=session,
        supplier_id=user.supplier.id,
        supplier_data_request=supplier_data_request,
        company_data_request=company_data_request,
    )

    return {
        "ok": True,
        "result": True,
    }
