from email.headerregistry import Address
from classes.response_models import *
from logic import utils
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, text, and_, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from logic.consts import *
from database import get_session
from database.models import *
import logging
from fastapi_jwt_auth import AuthJWT


suppliers = APIRouter()


@suppliers.get("/get-product-properties/",
               summary="")
async def get_product_properties(
    category_id: int,
    session: AsyncSession = Depends(get_session)
) -> JSONResponse:
    pass


@suppliers.get(
    "/get-supplier-info/",
    summary="",
    # response_model=SupplierAccountInfoOut
)
async def get_supplier_data_info(
    # Authorize: AuthJWT = Depends(),
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    # Authorize.jwt_required()
    # user_email = Authorize.get_jwt_subject()
    # user_id = await User.get_user_id(email=user_email)
    result = {}
    users_query = await session.execute(
        select(User.first_name, User.last_name, User.phone)\
        .where(User.id.__eq__(user_id))
    )
    personal_info: dict = dict(users_query.all()[0])
    country_registration = (await session.execute(
        select(UserAdress.country)\
        .where(UserAdress.user_id.__eq__(user_id))
    )).all()[0]
    country_registration: dict = dict(country_registration)
    license_number = (await session.execute(
        select(Supplier.license_number)\
        .where(Supplier.user_id.__eq__(user_id))
    )).all()[0]
    license_number: dict = dict(license_number)
    personal_info.update(country_registration)
    personal_info.update(license_number)
    
    supplier_id: int = await session.execute(
        select(Supplier.id)\
        .where(Supplier.user_id.__eq__(user_id))
    )
    supplier_id: int = supplier_id.scalar()
    company_query = dict((await session.execute(
        select(
            Company.logo_url,
            Company.name,
            Company.business_sector,
            Company.is_manufacturer,
            Company.year_established,
            Company.number_of_employees,
            Company.description,
            Company.phone,
            Company.business_email,
            Company.address
        )\
        .where(Company.supplier_id.__eq__(supplier_id))
    )).all()[0])
    photo_url_query = (await session.execute(
        select(CompanyImages.url)\
        .join(Company)
        .where(Company.supplier_id.__eq__(supplier_id))
    )).all()
    photo_url = dict(photo_url=[row["url"] for row in photo_url_query])
    company_query.update(photo_url)
    
    account_details_query = (await session.execute(
        select(UserCreds.password)\
        .where(UserCreds.user_id.__eq__(user_id))
    )).scalar()
    account_details = dict(account_details_query)

    return personal_info


@suppliers.post("/send-supplier-info/",
                summary="Is not tested with JWT")
async def send_supplier_data_info(
                               supplier_info: SupplierInfo,
                               account_info: SupplierAccountInfo,
                               Authorize: AuthJWT = Depends(),
                               session: AsyncSession = Depends(get_session)) -> JSONResponse:
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    user_id = await User.get_user_id(email=user_email)
    await session.execute(update(Supplier)\
                          .where(Supplier.user_id.__eq__(user_id))\
                          .values(license_number=supplier_info.tax_number))
    await session.commit()
    
    await session.execute(update(User)\
                          .where(User.id.__eq__(user_id))\
                          .values(first_name=supplier_info.first_name,
                                  last_name=supplier_info.last_name,
                                  phone=supplier_info.phone))
    await session.commit()

    supplier_data: UserAdress = UserAdress(user_id=user_id,
                               country=supplier_info.country)

    supplier_id: int = await session.execute(
        select(Supplier.id)\
        .where(Supplier.user_id.__eq__(user_id))
    )
    supplier_id: int = supplier_id.scalar()
    account_data: Company = Company(
        supplier_id=supplier_id,
        name=account_info.shop_name,
        business_sector=account_info.business_sector,
        logo_url=account_info.logo_url,
        is_manufacturer=account_info.is_manufacturer,
        year_established=account_info.year_established,
        number_of_employees=account_info.number_of_emploees,
        description=account_info.description,
        photo_url=account_info.photo_url,
        phone=account_info.business_phone,
        business_email=account_info.business_email,
        address=account_info.company_address
    )
    session.add_all((supplier_data, account_data))
    await session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "DATA_HAS_BEEN_SENT"}
    )


@suppliers.post("/add-product/",
                summary="")
async def add_new_product(
    a: MainProductInfo,
    session: AsyncSession = Depends(get_session)
):
    pass