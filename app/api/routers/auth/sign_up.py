from typing import Optional

from corecrud import Returning, Values, Where
from fastapi import APIRouter
from fastapi.background import BackgroundTasks
from fastapi.param_functions import Body, Depends, Path
from fastapi.responses import Response
from fastapi_mail import MessageSchema, MessageType
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core import exceptions
from core.app import aws_s3, crud, fm
from core.depends import (
    AuthJWT,
    Authorization,
    DatabaseSession,
    FileObjects,
    ImageOptional,
    SupplierAuthorization,
)
from core.depends.google_token import google_verifier
from core.security import create_access_token, generate_random_password, hash_password
from core.settings import application_settings, aws_s3_settings
from enums import UserType
from orm import (
    CompanyBusinessSectorToCategoryModel,
    CompanyModel,
    CompanyPhoneModel,
    CountryModel,
    SellerImageModel,
    SellerModel,
    SellerNotificationsModel,
    SupplierModel,
    SupplierNotificationsModel,
    UserCredentialsModel,
    UserModel,
)
from schemas import ApplicationResponse
from schemas.uploads import (
    BusinessSectorsUpload,
    CompanyDataUpload,
    CompanyPhoneDataUpload,
    RegisterUpload,
    SupplierDataUpload,
    TokenConfirmationUpload,
    UserDataUpload,
)
from typing_ import DictStrAny, RouteReturnT
from utils.cookies import set_and_create_tokens_cookies

router = APIRouter()


async def sign_up_core(request: RegisterUpload, user: UserModel, session: AsyncSession) -> None:
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
        supplier = await crud.suppliers.insert.one(
            Values({SupplierModel.user_id: user.id}),
            Returning(SupplierModel),
            session=session,
        )
        await crud.suppliers_notifications.insert.one(
            Values({SupplierNotificationsModel.supplier_id: supplier.id}),
            Returning(SupplierNotificationsModel.id),
            session=session,
        )
    else:
        seller = await crud.sellers.insert.one(
            Values({SellerModel.user_id: user.id}),
            Returning(SellerModel),
            session=session,
        )
        await crud.sellers_images.insert.one(
            Values(
                {SellerImageModel.seller_id: seller.id},
            ),
            Returning(SellerImageModel.id),
            session=session,
        )
        await crud.sellers_notifications.insert.one(
            Values({SellerNotificationsModel.seller_id: seller.id}),
            Returning(SellerNotificationsModel.id),
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
    path="/{user_type}",
    summary="WORKS: User registration.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def sign_up(
    authorize: AuthJWT,
    session: DatabaseSession,
    background_tasks: BackgroundTasks,
    request: RegisterUpload = Body(...),
    user_type: UserType = Path(...),
) -> RouteReturnT:
    if await crud.users.select.one(
        Where(UserModel.email == request.email.lower()),
        session=session,
    ):
        raise exceptions.AlreadyExistException(
            detail="Email is already registered",
        )

    user = await crud.users.insert.one(
        Values(
            {
                UserModel.email: request.email,
                UserModel.is_supplier: user_type == UserType.SUPPLIER,
                UserModel.is_verified: False,
            }
        ),
        Returning(UserModel),
        session=session,
    )
    await sign_up_core(request=request, user=user, session=session)
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


async def confirm_email_core(session: AsyncSession, user_id: int) -> None:
    await session.execute(
        update(UserModel).where(UserModel.id == user_id).values({UserModel.is_verified: True})
    )


@router.get(
    path="/confirmEmail",
    summary="WORKS: Processing token that was sent to user during the registration process.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def confirm_email(
    response: Response,
    session: DatabaseSession,
    authorize: AuthJWT,
    request: TokenConfirmationUpload = Depends(),
) -> RouteReturnT:
    try:
        user_id = authorize.get_raw_jwt(encoded_token=request.token)["sub"]
    except Exception:
        raise exceptions.ForbiddenException(detail="Invalid token")

    user = (
        await session.execute(select(UserModel).where(UserModel.id == user_id))
    ).scalar_one_or_none()

    if not user:
        raise exceptions.NotFoundException(detail="User not found")

    set_and_create_tokens_cookies(response=response, authorize=authorize, subject=user.id)
    await confirm_email_core(session=session, user_id=user.id)

    return {
        "ok": True,
        "result": True,
    }


async def send_account_info_core(
    session: AsyncSession,
    user_id: int,
    request: UserDataUpload,
) -> None:
    country = (
        await session.execute(select(CountryModel.id).where(CountryModel.id == request.country_id))
    ).scalar_one_or_none()
    if country is None:
        raise exceptions.NotFoundException(detail="Country with provided id does not exist")

    await session.execute(
        update(UserModel).where(UserModel.id == user_id).values(**request.dict())
    )


@router.post(
    path="/account/sendInfo",
    summary="WORKS: update UserModel with additional information (as part of the first step) such as: first_name, last_name, country_code, phone_number",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def send_account_info(
    user: Authorization,
    session: DatabaseSession,
    request: UserDataUpload = Body(...),
) -> RouteReturnT:
    await send_account_info_core(session=session, user_id=user.id, request=request)

    return {
        "ok": True,
        "result": True,
    }


async def send_business_info_core(
    session: AsyncSession,
    supplier_id: int,
    logo_image: FileObjects,
    supplier_data_request: SupplierDataUpload,
    company_data_request: CompanyDataUpload,
    business_sectors_request: BusinessSectorsUpload,
    company_phone_data_request: CompanyPhoneDataUpload,
) -> None:
    await crud.suppliers.update.one(
        Values(supplier_data_request.dict()),
        Where(SupplierModel.id == supplier_id),
        Returning(SupplierModel.id),
        session=session,
    )

    company_id = await crud.companies.insert.one(
        Values(
            {
                CompanyModel.supplier_id: supplier_id,
            }
            | company_data_request.dict(),
        ),
        Returning(CompanyModel.id),
        session=session,
    )

    await crud.companies_business_sectors_to_categories.insert.many(
        Values(
            [
                {
                    CompanyBusinessSectorToCategoryModel.category_id: business_sector,
                    CompanyBusinessSectorToCategoryModel.company_id: company_id,
                }
                for business_sector in business_sectors_request.business_sectors
            ]
        ),
        Returning(CompanyBusinessSectorToCategoryModel),
        session=session,
    )

    if company_phone_data_request:
        await crud.companies_phones.insert.one(
            Values(
                {
                    CompanyPhoneModel.company_id: company_id,
                }
                | company_phone_data_request.dict(),
            ),
            Returning(CompanyPhoneModel.id),
            session=session,
        )

    if logo_image:
        link = await aws_s3.upload_file_to_s3(
            bucket_name=aws_s3_settings.S3_COMPANY_IMAGES_BUCKET, file=logo_image
        )

        await crud.companies.update.one(
            Values(
                {CompanyModel.logo_url: link},
            ),
            Where(CompanyModel.id == company_id),
            Returning(CompanyModel.logo_url),
            session=session,
        )


@router.post(
    path="/business/sendInfo",
    summary="WORKS: update SupplierModel with licence information & creates CompanyModel",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def send_business_info(
    user: SupplierAuthorization,
    session: DatabaseSession,
    logo_image: ImageOptional,
    supplier_data_request: SupplierDataUpload = Body(...),
    company_data_request: CompanyDataUpload = Body(...),
    business_sectors_request: BusinessSectorsUpload = Body(...),
    company_phone_data_request: Optional[CompanyPhoneDataUpload] = Body(...),
) -> RouteReturnT:
    if user.supplier.company:
        raise exceptions.AlreadyExistException(detail="Supplier is already has company")

    await send_business_info_core(
        session=session,
        supplier_id=user.supplier.id,
        logo_image=logo_image,
        supplier_data_request=supplier_data_request,
        company_data_request=company_data_request,
        business_sectors_request=business_sectors_request,
        company_phone_data_request=company_phone_data_request,
    )

    return {
        "ok": True,
        "result": True,
    }


async def google_sign_up_core(google_user_info, user_type, session: AsyncSession) -> UserModel:
    user = (
        await session.execute(
            insert(UserModel)
            .values(
                {
                    UserModel.email: google_user_info["email"],
                    UserModel.first_name: google_user_info["given_name"],
                    UserModel.last_name: google_user_info["family_name"],
                    UserModel.is_supplier: user_type == UserType.SUPPLIER,
                    UserModel.is_verified: True,
                }
            )
            .returning(UserModel)
        )
    ).scalar_one()
    await session.execute(
        insert(UserCredentialsModel).values(
            {
                UserCredentialsModel.user_id: user.id,
                UserCredentialsModel.password: hash_password(password=generate_random_password()),
            }
        )
    )
    if user.is_supplier and (user_type == UserType.SUPPLIER):
        supplier = (
            await session.execute(
                insert(SupplierModel)
                .values(
                    {
                        SupplierModel.user_id: user.id,
                    }
                )
                .returning(SupplierModel)
            )
        ).scalar_one()
        await session.execute(
            insert(SupplierNotificationsModel).values(
                {
                    SupplierNotificationsModel.supplier_id: supplier.id,
                    SupplierNotificationsModel.on_advertising_campaigns: True,
                    SupplierNotificationsModel.on_order_updates: True,
                    SupplierNotificationsModel.on_order_reminders: True,
                    SupplierNotificationsModel.on_product_updates: True,
                    SupplierNotificationsModel.on_product_reminders: True,
                    SupplierNotificationsModel.on_reviews_of_products: True,
                    SupplierNotificationsModel.on_change_in_demand: True,
                    SupplierNotificationsModel.on_advice_from_abra: True,
                    SupplierNotificationsModel.on_account_support: True,
                }
            )
        )
    else:
        seller = (
            await session.execute(
                insert(SellerModel)
                .values(
                    {
                        SellerModel.user_id: user.id,
                    }
                )
                .returning(SellerModel)
            )
        ).scalar_one()
        await session.execute(
            insert(SellerNotificationsModel).values(
                {
                    SellerNotificationsModel.seller_id: seller.id,
                    SellerNotificationsModel.on_discount: True,
                    SellerNotificationsModel.on_order_updates: True,
                    SellerNotificationsModel.on_order_reminders: True,
                    SellerNotificationsModel.on_stock_again: True,
                    SellerNotificationsModel.on_product_is_cheaper: True,
                    SellerNotificationsModel.on_your_favorites_new: True,
                    SellerNotificationsModel.on_account_support: True,
                }
            )
        )
    return user


@router.post(
    path="/google/{user_type}",
    summary="WORKS: Google sign up.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def google_sign_up(
    response: Response,
    authorize: AuthJWT,
    session: DatabaseSession,
    user_type: UserType = Path(...),
    google_user_info: DictStrAny = Depends(google_verifier.verify_google_token),
) -> RouteReturnT:
    user = (
        await session.execute(
            select(UserModel).where(
                UserModel.email == google_user_info["email"],
            )
        )
    ).scalar_one_or_none()
    if not user:
        user = await google_sign_up_core(
            google_user_info=google_user_info, user_type=user_type, session=session
        )
        set_and_create_tokens_cookies(response=response, authorize=authorize, subject=user.id)
    elif (user_type == UserType.SUPPLIER) and user.is_supplier:
        set_and_create_tokens_cookies(response=response, authorize=authorize, subject=user.id)
    else:
        raise exceptions.AlreadyExistException(detail="User already exists")

    return {
        "ok": True,
        "result": True,
    }
