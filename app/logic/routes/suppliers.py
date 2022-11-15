import logging
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
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session)
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    user_id = await User.get_user_id(email=user_email)
    result = dict()

    personal_info = await session.execute(
        select(User.first_name, User.last_name, User.phone)
        .where(User.id.__eq__(user_id))
    )
    personal_info = personal_info.fetchone()
    if not personal_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="USER_DATA_IS_MISSING"
        )
    personal_info = dict(personal_info)

    country_registration = await session.execute(
        select(UserAdress.country)
        .where(UserAdress.user_id.__eq__(user_id))
    )
    country_registration = country_registration.fetchone()
    if not country_registration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="USER_ADRESS_DATA_IS_MISSING"
        )
    country_registration = dict(country_registration)

    license_number = await session.execute(
        select(Supplier.license_number)
        .where(Supplier.user_id.__eq__(user_id))
    )
    license_number = license_number.fetchone()
    if not license_number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SUPPLIER_DATA_IS_MISSING"
        )
    license_number = dict(license_number)

    personal_info['email'] = user_email
    personal_info.update(country_registration)
    personal_info.update(license_number)

    supplier_id = await Supplier.get_supplier_id(user_id=user_id)
    business_profile = await session.execute(
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
        )
        .where(Company.supplier_id.__eq__(supplier_id))
    )
    business_profile = business_profile.fetchone()
    if not business_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="COMPANY_DATA_IS_MISSING"
        )
    business_profile = dict(business_profile)

    photo_url = await session.execute(
        select(CompanyImages.url)
        .join(Company)
        .where(Company.supplier_id.__eq__(supplier_id))
    )
    photo_url = photo_url.fetchall()
    if not photo_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="COMPANY_IMAGES_DATA_IS_MISSING"
        )
    photo_url = dict(url=[row['url'] for row in photo_url])
    business_profile.update(photo_url)

    result = dict(
        personal_info=personal_info,
        business_profile=business_profile
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": result}
    )


@suppliers.post("/send_account_info/",
                summary="Is not tested with JWT")
async def send_supplier_data_info(
        user_info: SupplierUserData,
        license: SupplierLicense,
        company_info: SupplierCompanyData,
        country: SupplierCountry,
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_session)) -> JSONResponse:
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    user_id = await User.get_user_id(email=user_email)
    supplier_id: int = await session.execute(
        select(Supplier.id)
        .where(Supplier.user_id.__eq__(user_id))
    )
    supplier_id: int = supplier_id.scalar()

    user_data: dict = {key: value for key, value in dict(user_info).items() if value}
    license_data: dict = {key: value for key, value in dict(license).items() if value}
    company_data: dict = {key: value for key, value in dict(company_info).items() if value}
    country_data: dict = {key: value for key, value in dict(country).items() if value}

    await session.execute(
        update(User)
        .where(User.id.__eq__(user_id))
        .values(**(user_data))
    )
    await session.execute(
        update(Supplier)
        .where(Supplier.user_id.__eq__(user_id))
        .values(**(license_data))
    )
    await session.execute(
        update(Company)
        .where(Company.supplier_id.__eq__(supplier_id))
        .values(**(company_data))
    )
    await session.execute(
        update(UserAdress)
        .where(UserAdress.user_id.__eq__(user_id))
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
    properties_raw_data = [dict(row) for row in properties_sql_data if row]
    if not properties_raw_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PROPERTIES_NOT_FOUND"
        )
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
    variations_sql_data = await session\
        .execute(text(QUERY_TO_GET_VARIATIONS.format(category_id=category_id)))
    variations_raw_data = [dict(row) for row in variations_sql_data if row]
    if not variations_raw_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VARIATIONS_NOT_FOUND"
        )
    json_variations = dict()
    for row in variations_raw_data:
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

    try:
        product_id = await session\
            .execute(select(func.max(Product.id))
                     .where(and_(Product.supplier_id.__eq__(supplier_id),
                                 Product.name.__eq__(product_info.product_name))))
        product_id = product_id.scalar()

        for property in properties:
            category_property_type_id = await session\
                .execute(select(CategoryPropertyType.id)
                         .where(CategoryPropertyType.name.__eq__(property.name)))
            category_property_type_id = category_property_type_id.scalar()
            if not category_property_type_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=dict(error="PROPERTY_NOT_FOUND", name=property.name)
                )
            is_property_match_category = await session\
                .execute(select(CategoryProperty.id)
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
                .execute(select(CategoryVariation.variation_type_id)
                         .join(CategoryVariationType)
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
                if not variation.count:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=dict(error="COUNT_IS_NOT_PROVIDED", value=variation.value)
                    )
                product_variations_count = ProductVariationCount(
                    product_variation_value1_id=product_variation_value_id_parent,
                    count=variation.count
                )
                session.add(product_variations_count)
            else:
                for child_variation in variation.childs:
                    if not child_variation.count:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=dict(
                                error="COUNT_IS_NOT_PROVIDED",
                                value=dict(
                                    value=variation.value,
                                    child_variation=child_variation.value
                                )
                            )
                        )
                    category_variation_type_id = await session\
                        .execute(select(CategoryVariation.variation_type_id)
                                 .join(CategoryVariationType)
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

        product_price_all_quantities = [price.quantity for price in prices]
        if len(product_price_all_quantities) != len(set(product_price_all_quantities)):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="NOT_UNIQUE_QUANTITIES_PROVIDED"
            )
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
    except Exception as error:
        if 'product_variation_value_id_parent' in locals():
            await session.execute(delete(ProductVariationCount)
                                  .where(ProductVariationCount.product_variation_value1_id.__eq__(product_variation_value_id_parent)))
        if 'product_id' in locals():
            await session.execute(delete(ProductVariationValue)
                                  .where(ProductVariationValue.product_id.__eq__(product_id)))
            await session.execute(delete(ProductPropertyValue)
                                  .where(ProductPropertyValue.product_id.__eq__(product_id)))
        if 'category_property_type_id' in locals():
            await session.execute(delete(CategoryPropertyValue)
                                  .where(CategoryPropertyValue.property_type_id.__eq__(category_property_type_id)))
        if 'product_id' in locals():
            await session.execute(delete(ProductPrice)
                                  .where(ProductPrice.product_id.__eq__(product_id)))
            await session.execute(delete(Product)
                                  .where(Product.id.__eq__(product_id)))
        await session.commit()
        raise error


@suppliers.post("/manage_products/",
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


@suppliers.patch("/delete_products/",
                 summary="WORKS: Delete products (change is_active to 0).",
                 response_model=ProductIdOut)
async def get_supplier_products(products: List[int],
                                product_list_in_output: bool = True,
                                Authorize: AuthJWT = Depends(),
                                session: AsyncSession = Depends(get_session)):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())['email']
    supplier_id = await Supplier.get_supplier_id_by_email(email=user_email)
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
        await session.execute(update(Product)
                              .where(Product.id.__eq__(product_id))
                              .values(is_active=0))
    await session.commit()

    if product_list_in_output:
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
    else:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": "OK"}
        )


# Possible improvement - async upload https://aioboto3.readthedocs.io/en/latest/usage.html
@suppliers.post(
    "/upload_product_image/",
    summary="WORKS: Uploads provided product image to AWS S3 and saves url to DB",
)
async def upload_product_image(
    file: UploadFile,
    product_id: int,
    serial_number: int,
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    authorize.jwt_required()

    url = await utils.upload_file_to_s3(bucket=AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET, file=file)

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


@suppliers.post(
    "/upload_logo_image/",
    summary="WORKS: Uploads provided logo image to AWS S3 and saves url to DB",
)
async def upload_file_to_s3(
    file: UploadFile,
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    authorize.jwt_required()
    user_email = json.loads(authorize.get_jwt_subject())['email']
    user_id = await User.get_user_id(email=user_email)
    url = await utils.upload_file_to_s3(bucket=AWS_S3_IMAGE_USER_LOGO_BUCKET, file=file)

    # Upload data to DB
    existing_row = await session.execute(
        select(UserImage.id).where(
            and_(
                UserImage.user_id == user_id,
                UserImage.source_url == url,
            )
        )
    )
    existing_row = existing_row.scalar()

    if existing_row is None:
        await session.execute(
            insert(UserImage).values(
                user_id=user_id,
                source_url=url,
                thumbnail_url=url
            )
        )
        logging.info(
            "User logo is written to DB: user_id='%s', image_url='%s'",
            user_id,
            url,
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
        .execute(select(Company.name, Company.logo_url)
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
