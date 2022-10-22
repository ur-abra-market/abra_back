import hashlib
import imghdr
import logging
import os
#import boto3
from app.classes.response_models import *
from app.database import get_session
from app.database.models import *
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from app.logic import utils
from app.logic.consts import *
from sqlalchemy import and_, delete, insert, or_, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
import json


suppliers = APIRouter()


@suppliers.get(
    "/get_supplier_info/",
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
    users_query: dict = dict(users_query.all()[0])
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
    users_query.update(country_registration)
    users_query.update(license_number)
    
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
    )).all()[0]
    user_email = "email"
    account_details_query = dict(account_details_query, email=user_email)

    result = dict(
        personal_info=users_query,
        business_profile=company_query,
        account_details=account_details_query
    )

    return result


# @suppliers.post("/send-account-info/",
#                 summary="Is not tested with JWT")
# async def send_supplier_data_info(
#                                supplier_info: SupplierInfo,
#                                account_info: SupplierAccountInfo,
#                                Authorize: AuthJWT = Depends(),
#                                session: AsyncSession = Depends(get_session)) -> JSONResponse:
#     Authorize.jwt_required()
#     user_email = Authorize.get_jwt_subject()
#     user_id = await User.get_user_id(email=user_email)
#     await session.execute(update(Supplier)\
#                           .where(Supplier.user_id.__eq__(user_id))\
#                           .values(license_number=supplier_info.tax_number))
#     await session.commit()
    
#     await session.execute(update(User)\
#                           .where(User.id.__eq__(user_id))\
#                           .values(first_name=supplier_info.first_name,
#                                   last_name=supplier_info.last_name,
#                                   phone=supplier_info.phone))
#     await session.commit()

#     supplier_data: UserAdress = UserAdress(user_id=user_id,
#                                country=supplier_info.country)

#     supplier_id: int = await session.execute(
#         select(Supplier.id)\
#         .where(Supplier.user_id.__eq__(user_id))
#     )
#     supplier_id: int = supplier_id.scalar()
#     account_data: Company = Company(
#         supplier_id=supplier_id,
#         name=account_info.shop_name,
#         business_sector=account_info.business_sector,
#         logo_url=account_info.logo_url,
#         is_manufacturer=account_info.is_manufacturer,
#         year_established=account_info.year_established,
#         number_of_employees=account_info.number_of_emploees,
#         description=account_info.description,
#         photo_url=account_info.photo_url,
#         phone=account_info.business_phone,
#         business_email=account_info.business_email,
#         address=account_info.company_address
#     )
#     session.add_all((supplier_data, account_data))
#     await session.commit()

#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content={"result": "DATA_HAS_BEEN_SENT"}
#     )


@suppliers.post("/send_account_info/",
                summary="Is not tested with JWT")
async def send_supplier_data_info(
                            #    supplier_info: SupplierInfo,
                            #    account_info: SupplierAccountInfo,
                            #    Authorize: AuthJWT = Depends(),
                            user_id: int,
                            supplier_id: int,
                            user_info: SupplierUserData,
                            license: SupplierLicense,
                            company_info: SupplierCompanyData,
                            country: SupplierCountry,
                            session: AsyncSession = Depends(get_session)) -> JSONResponse:
    # Authorize.jwt_required()
    # user_email = Authorize.get_jwt_subject()
    # user_id = await User.get_user_id(email=user_email)

    user_data: dict = {key: value for key, value in dict(user_info).items() if value}
    license_data: dict = {key: value for key, value in dict(license).items() if value}
    company_data: dict = {key: value for key, value in dict(company_info).items() if value}
    country_data: dict = {key: value for key, value in dict(country).items() if value}

    await session.execute(
        update(User)\
        .where(User.id.__eq__(user_id))\
        .values(**(user_data))
    )
    await session.execute(
        update(Supplier)\
        .where(Supplier.user_id.__eq__(user_id))\
        .values(**(license_data))
    )
    await session.execute(
        update(Company)\
        .where(Company.supplier_id.__eq__(supplier_id))\
        .values(**(company_data))
    )
    await session.execute(
        update(UserAdress)\
        .where(UserAdress.user_id.__eq__(user_id))\
        .values(**(country_data))
    )
    await session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "DATA_HAS_BEEN_SENT"}
    )


@suppliers.get("/get_product_properties/",
    summary="WORKS (ex. 1): Get all property names by category_id.",
    response_model=ResultListOut)
async def get_product_properties_from_db(category_id: int,
                                session: AsyncSession = Depends(get_session)):
    is_category_exist = await Category.is_category_id_exist(category_id=category_id)
    if not is_category_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GATEGORY_ID_DOES_NOT_EXIST"
        )
    properties_sql_data = await session\
        .execute(text(QUERY_TO_GET_PROPERTIES.format(category_id=category_id)))
    if not properties_sql_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PROPERTIES_NOT_FOUND"
        )
    properties_raw_data = [dict(row) for row in properties_sql_data]
    unique_property_names = list(set(row['name'] for row in properties_raw_data))
    json_result = [dict(key=name, values=[]) for name in unique_property_names]
    for row in properties_raw_data:
        for json_row in json_result:
            if json_row['key'] == row['name']:
                json_row['values'].append(dict(value=row['value'], optional_value=row['optional_value']))
                break
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": json_result}
    )
    

@suppliers.get("/get_product_variations/",
    summary="WORKS (ex. 1): Get all variation names and values by category_id.",
    response_model=ResultListOut)
async def get_product_variations_from_db(category_id: int,
                                         session: AsyncSession = Depends(get_session)):
    is_category_exist = await Category.is_category_id_exist(category_id=category_id)
    if not is_category_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GATEGORY_ID_DOES_NOT_EXIST"
        )
    variations = await session\
        .execute(text(QUERY_TO_GET_VARIATIONS.format(category_id=category_id)))
    if not variations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VARIATIONS_NOT_FOUND"
        )
    variations = [dict(row) for row in variations]
    json_variations = dict()
    for row in variations:
        if row['name'] not in json_variations:
            json_variations[row['name']] = list()
        json_variations[row['name']].append(row['value'])

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": json_variations}
    )


@suppliers.post("/add_product/",
    summary="WORKS: Add product to database.",
    response_model=ProductIdOut)
async def add_product_info_to_db(product_info: ProductInfo,
                            properties: List[PropertiesDict],
                            variations: List[VariationsDict],
                            prices: List[ProductPrices],
                            Authorize: AuthJWT = Depends(),
                            session: AsyncSession = Depends(get_session)):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())['email']
    if not prices:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PRODUCT_PRICES_IS_EMPTY"
        )
    user_id = await User.get_user_id(email=user_email)
    supplier_id = await Supplier.get_supplier_id(user_id=user_id)
    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT_SUPPLIER"
        )
    category_id = product_info.category_id
    is_category_id_exist = await Category.is_category_id_exist(category_id=category_id)
    if not is_category_id_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GATEGORY_ID_DOES_NOT_EXIST"
        )
    current_datetime = utils.get_moscow_datetime()
    product = Product(
        supplier_id=supplier_id,
        category_id=category_id,
        name=product_info.product_name,
        description=product_info.description,
        datetime=current_datetime,
        UUID=''
    )
    session.add(product)
    await session.commit()
    product_id = await session\
                .execute(select(func.max(Product.id))\
                .where(and_(Product.supplier_id.__eq__(supplier_id),
                            Product.name.__eq__(product_info.product_name))))
    product_id = product_id.scalar()

    for property in properties:
        category_property_type_id = await session\
            .execute(select(CategoryPropertyType.id)\
            .where(CategoryPropertyType.name.__eq__(property.name)))
        category_property_type_id = category_property_type_id.scalar()
        if not category_property_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="PROPERTY_NOT_FOUND", name=property.name)
            )
        is_property_match_category = await session\
            .execute(select(CategoryProperty.id)\
            .where(and_(CategoryProperty.category_id.__eq__(category_id),
                        CategoryProperty.property_type_id.__eq__(category_property_type_id))))
        is_property_match_category = bool(is_property_match_category.scalar())
        if not is_property_match_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="PROPERTY_DOES_NOT_MATCH_CATEGORY", name=property.name)
            )
        category_property_value_id = await CategoryPropertyValue.get_category_property_value_id(
                                            category_property_type_id=category_property_type_id,
                                            value=property.value,
                                            optional_value=property.optional_value)            
        if not category_property_value_id:
            category_property_value = CategoryPropertyValue(
                property_type_id=category_property_type_id,
                value=property.value,
                optional_value=property.optional_value
            )
            session.add(category_property_value)
            await session.commit()
            category_property_value_id = await CategoryPropertyValue.get_category_property_value_id(
                                                category_property_type_id=category_property_type_id,
                                                value=property.value,
                                                optional_value=property.optional_value) 
        product_property_value = ProductPropertyValue(
            product_id=product_id,
            property_value_id=category_property_value_id
        )
        session.add(product_property_value)
    
    for variation in variations:
        category_variation_type_id = await session\
            .execute(select(CategoryVariation.variation_type_id)\
            .join(CategoryVariationType)\
            .where(and_(CategoryVariationType.name.__eq__(variation.name),
                        CategoryVariation.category_id.__eq__(category_id))))
        category_variation_type_id = category_variation_type_id.scalar()
        if not category_variation_type_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="VARIATION_NAME_DOES_NOT_EXIST", name=variation.name)
            )
        category_variation_value_id = await CategoryVariationValue.get_category_variation_value_id(
                                                    category_variation_type_id=category_variation_type_id,
                                                    value=variation.value)
        if not category_variation_value_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="VARIATION_VALUE_DOES_NOT_EXIST", value=variation.value)
            )
        product_variation_value_id_parent = await ProductVariationValue.get_product_variation_value_id(product_id=product_id,
                                                                    category_variation_value_id=category_variation_value_id)
        if not product_variation_value_id_parent:
            product_variation_value = ProductVariationValue(
                product_id=product_id,
                variation_value_id=category_variation_value_id
            )
            session.add(product_variation_value)
            await session.commit()
            product_variation_value_id_parent = await ProductVariationValue.get_product_variation_value_id(product_id=product_id,
                                                                    category_variation_value_id=category_variation_value_id)
        if not variation.childs:
            product_variations_count = ProductVariationCount(
                product_variation_value1_id=product_variation_value_id_parent,
                count=variation.count
            )
            session.add(product_variations_count)
        else:
            for child_variation in variation.childs:
                category_variation_type_id = await session\
                    .execute(select(CategoryVariation.variation_type_id)\
                    .join(CategoryVariationType)\
                    .where(and_(CategoryVariationType.name.__eq__(child_variation.name),
                                CategoryVariation.category_id.__eq__(category_id))))
                category_variation_type_id = category_variation_type_id.scalar()
                if not category_variation_type_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=dict(error="VARIATION_NAME_DOES_NOT_EXIST", name=child_variation.name)
                    )
                category_variation_value_id = await CategoryVariationValue.get_category_variation_value_id(
                                                    category_variation_type_id=category_variation_type_id,
                                                    value=child_variation.value)
                if not category_variation_value_id:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=dict(error="VARIATION_VALUE_DOES_NOT_EXIST", value=child_variation.value)
                    )
                product_variation_value_id_child = await ProductVariationValue.get_product_variation_value_id(product_id=product_id,
                                                                    category_variation_value_id=category_variation_value_id)
                if not product_variation_value_id_child:
                    product_variation_value = ProductVariationValue(
                        product_id=product_id,
                        variation_value_id=category_variation_value_id
                    )
                    session.add(product_variation_value)
                    await session.commit()
                    product_variation_value_id_child = await ProductVariationValue.get_product_variation_value_id(product_id=product_id,
                                                                    category_variation_value_id=category_variation_value_id)
                product_variations_count = ProductVariationCount(
                    product_variation_value1_id=product_variation_value_id_parent,
                    product_variation_value2_id=product_variation_value_id_child,
                    count=child_variation.count
                )
                session.add(product_variations_count)

    for price in prices:
        product_price = ProductPrice(
            product_id=product_id,
            value=price.value,
            min_quantity=price.quantity
        )
        session.add(product_price)
    await session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"product_id": product_id}
    )


@suppliers.get("/manage_products/",
    summary="WORKS: Get list of all suppliers products.",
    response_model=ProductIdOut)
async def get_supplier_products(Authorize: AuthJWT = Depends(),
                            session: AsyncSession = Depends(get_session)):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())['email']
    user_id = await User.get_user_id(email=user_email)
    supplier_id = await Supplier.get_supplier_id(user_id=user_id)
    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT_SUPPLIER"
        )
    products = await session\
        .execute(text(QUERY_SUPPLIER_PRODUCTS.format(supplier_id=supplier_id)))
    products = [dict(row) for row in products]
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PRODUCTS_NOT_FOUND"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": products}
    )


@suppliers.delete("/delete_products/",
    summary="WORKS: Delete products (change is_active to 0).",
    response_model=ProductIdOut)
async def get_supplier_products(products: List[int],
                                Authorize: AuthJWT = Depends(),
                                session: AsyncSession = Depends(get_session)):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())['email']
    user_id = await User.get_user_id(email=user_email)
    supplier_id = await Supplier.get_supplier_id(user_id=user_id)
    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT_SUPPLIER"
        )
    for product_id in products:
        is_product_match_supplier = await Product.is_product_match_supplier(product_id=product_id,
                                                                            supplier_id=supplier_id)
        if not is_product_match_supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="PRODUCT_DOES_NOT_BELONG_SUPPLIER", product_id=product_id)
            )
        is_product_active = await Product.is_product_active(product_id=product_id)
        if not is_product_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(error="PRODUCT_ALREADY_DELETED", product_id=product_id)
            )
        await session.execute(update(Product)\
            .where(Product.id.__eq__(product_id))\
            .values(is_active=0))
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "OK"}
    )


# Possible improvement - async upload https://aioboto3.readthedocs.io/en/latest/usage.html
@suppliers.post(
    "/upload_image/",
    summary="WORKS: Uploads provided image to AWS S3 and saves url to DB",
)
async def upload_file_to_s3(
    file: UploadFile,
    product_id: int,
    serial_number: int,
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    authorize.jwt_required()

    bucket = os.getenv("AWS_BUCKET")
    _, file_extension = os.path.splitext(file.filename)
    contents = await file.read()
    filehash = hashlib.md5(contents)
    filename = str(filehash.hexdigest())

    # Validate file if it is image
    if not imghdr.what("", h=contents):
        logging.error("File is not an image: '%s'", file.filename)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_IMAGE")

    # Upload file to S3
    s3_client = boto3.client("s3")
    key = f"{filename[:2]}/{filename}{file_extension}"
    s3_client.upload_fileobj(file.file, bucket, key)
    url = f"https://{bucket}.s3.amazonaws.com/{key}"
    logging.info("File is uploaded to S3 by path: '%s'", f"s3://{bucket}/{key}")

    # Upload data to DB
    existing_row = await session.execute(
        select(ProductImage.id).where(
            and_(
                ProductImage.product_id == product_id,
                ProductImage.image_url == url,
                ProductImage.serial_number == serial_number,
            )
        )
    )
    existing_row = existing_row.scalar()

    if existing_row is None:
        await session.execute(
            insert(ProductImage).values(
                product_id=product_id, image_url=url, serial_number=serial_number
            )
        )
        logging.info(
            "Record is written to DB: product_id='%s', image_url='%s', serial_number='%s'",
            product_id,
            url,
            serial_number,
        )

    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "IMAGE_LOADED_SUCCESSFULLY"},
    )



@suppliers.get("/company_info/",
                summary="WORKS: Get company info (name, logo_url) by token.",
                response_model=CompanyInfo)
async def get_supplier_company_info(Authorize: AuthJWT = Depends(),
                                session: AsyncSession = Depends(get_session)):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())['email']
    user_id = await User.get_user_id(email=user_email)
    supplier_id = await Supplier.get_supplier_id(user_id=user_id)
    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT_SUPPLIER"
        )
    company_info = await session\
        .execute(select(Company.name, Company.logo_url)\
        .where(Company.supplier_id.__eq__(supplier_id)))
    result = None
    for row in company_info:
        result = dict(row)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="COMPANY_NOT_FOUND"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": result},
    )



# Example of possible solution for caching
# Library - https://github.com/long2ice/fastapi-cache
# import time
# from fastapi_cache import FastAPICache
# from fastapi_cache.decorator import cache
# from fastapi_cache.backends.inmemory import InMemoryBackend


# @app.on_event("startup")
# async def startup():
#     FastAPICache.init(InMemoryBackend())


# @suppliers.post("/cached_endpoint/")
# @cache(expire=60, namespace="test")
# async def cached_endpoint(msg: str):
#     time.sleep(5)
#     return msg


# @suppliers.get("/clear")
# async def clear():
#     return await FastAPICache.clear(namespace="test")
