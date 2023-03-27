from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ValidationError
from app.logic import utils
from sqlalchemy import func
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from sqlalchemy import select, text, and_, update, delete, func, insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.logic.consts import *
from app.logic.queries import *
from app.database import get_session
from app.database.models import *
from app.classes.response_models import ResultOut
import logging
from fastapi_jwt_auth import AuthJWT
from app.settings import (
    AWS_S3_COMPANY_IMAGES_BUCKET,
    AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
)
import os
import json


class SupplierInfo(BaseModel):
    first_name: str
    last_name: str
    country: str
    phone: str
    tax_number: int


class SupplierAccountInfo(BaseModel):
    logo_url: Optional[str] = None
    shop_name: str
    business_sector: str
    is_manufacturer: int
    year_established: Optional[int] = None
    number_of_emploees: Optional[int] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None
    business_phone: Optional[str] = None
    business_email: Optional[EmailStr] = None
    company_address: Optional[str] = None


class ProductIdOut(BaseModel):
    product_id: int


class ResultListOut(BaseModel):
    result: List[str]


class PropertiesDict(BaseModel):
    name: str
    value: str
    optional_value: Optional[str]


class VariationsChildDict(BaseModel):
    name: str
    value: str
    count: int


class VariationsDict(BaseModel):
    name: str
    value: str
    count: Optional[int]
    childs: Optional[List[VariationsChildDict]]


class ProductInfo(BaseModel):
    product_name: str
    category_id: int
    description: Optional[str]


class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    personal_number: str
    license_number: str


class BusinessProfile(BaseModel):
    logo_url: str
    shop_name: str
    business_sector: str
    is_manufacturer: int
    year_established: int
    number_of_employees: int
    description: str
    photo_url: List[str]
    phone: str
    business_email: EmailStr
    adress: str


class AccountDetails(BaseModel):
    email: EmailStr
    password: str


class SupplierAccountInfoOut(BaseModel):
    personal_info: PersonalInfo
    business_profile: BusinessProfile
    account_details: AccountDetails


class SupplierUserData(BaseModel):
    first_name: str
    last_name: Optional[str]
    phone: str = Field(None, alias="user_phone")


class SupplierLicense(BaseModel):
    license_number: int


class SupplierCompanyData(BaseModel):
    name: str
    business_sector: str
    is_manufacturer: int
    year_established: Optional[int]
    number_of_employees: Optional[int]
    description: Optional[str]
    phone: Optional[str]
    business_email: Optional[EmailStr]
    address: Optional[str]


class ProductPrices(BaseModel):
    value: float
    quantity: int


class CompanyInfo(BaseModel):
    name: str
    logo_url: str


class SupplierPersonalProfile(PersonalInfo):
    email: EmailStr
    license_number: int


class BusinessProfile(SupplierCompanyData):
    phone: str = Field(alias="company_phone")
    business_email: EmailStr
    address: str


class SupplierInfoResponse(BaseModel):
    personal_info: SupplierPersonalProfile
    business_profile: BusinessProfile


suppliers = APIRouter()


@suppliers.get(
    "/get_supplier_info/",
    summary="WORKS: Get supplier info (presonal and business).",
    response_model=SupplierInfoResponse,
)
async def get_supplier_data_info(
        Authorize: AuthJWT = Depends(),
        session: AsyncSession = Depends(get_session)
) -> SupplierInfoResponse:
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    user_id = await User.get_user_id(email=user_email)
    query = (
        select(
            User.first_name,
            User.last_name,
            User.phone.label("personal_number"),
            Supplier.license_number,
            Company.logo_url,
            Company.name,
            Company.business_sector,
            Company.is_manufacturer,
            Company.year_established,
            Company.number_of_employees,
            Company.description,
            Company.phone.label("company_phone"),
            Company.business_email,
            Company.address,
            func.group_concat(CompanyImages.url, "|").label("images_url"),
        )
        .outerjoin(Supplier, Supplier.user_id == User.id)
        .outerjoin(Company, Company.supplier_id == Supplier.id)
        .outerjoin(CompanyImages, CompanyImages.company_id == Company.id)
        .filter(User.id == user_id)
        .group_by(
            # group all the fields to fetch and concatenate rows from One2Many tables
            # for example CompanyImages
            User.first_name,
            User.last_name,
            User.phone.label("personal_number"),
            Supplier.license_number,
            Company.logo_url,
            Company.name,
            Company.business_sector,
            Company.is_manufacturer,
            Company.year_established,
            Company.number_of_employees,
            Company.description,
            Company.phone.label("company_phone"),
            Company.business_email,
            Company.address,
        )
    )

    res = await session.execute(query)
    data_dict = dict(res.fetchone())
    if data_dict["images_url"]:
        data_dict["images_url"] = [e for e in data_dict["images_url"].split("|") if e]
    data_dict["email"] = user_email

    # exmample of validation errors
    # as_dict.pop('logo_url')
    # as_dict['is_manufacturer'] = 'some wrong value'

    try:
        personal_info = SupplierPersonalProfile(**data_dict)
        business_profile = BusinessProfile(**data_dict)
        result = {
            "result": {
                "personal_info": personal_info.dict(),
                "business_profile": business_profile.dict(),
            }
        }
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except ValidationError as ex:
        # put all validation errors into response
        message = " | ".join([":".join([e["msg"], e["loc"][0]]) for e in ex.errors()])
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


@suppliers.patch(
    "/send_account_info/",
    summary="WORKS: Should be discussed. "
    "'images_url' insert images in company_images, "
    "other parameters update corresponding values.",
    response_model=ResultOut,
)
async def send_supplier_data_info(
    user_info: SupplierUserData,
    license: SupplierLicense,
    company_info: SupplierCompanyData,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
) -> JSONResponse:
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    # next two queries must be united in the future
    user_id = await User.get_user_id(email=user_email)
    supplier_id = await Supplier.get_supplier_id_by_email(email=user_email)

    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="USER_NOT_FOUND"
        )

    company_info = dict(company_info)
    user_data: dict = {key: value for key, value in dict(user_info).items() if value}
    license_data: dict = {key: value for key, value in dict(license).items()}
    company_data: dict = {key: value for key, value in company_info.items() if value}

    await session.execute(
        update(User).where(User.id.__eq__(user_id)).values(**user_data)
    )
    await session.execute(
        update(Supplier)
        .where(Supplier.user_id.__eq__(user_id))
        .values(**license_data)
    )
    await session.execute(
        update(Company)
        .where(Company.supplier_id.__eq__(supplier_id))
        .values(**company_data)
    )
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "DATA_HAS_BEEN_SENT"}
    )


@suppliers.get(
    "/get_product_properties/{category_id}/",
    summary="WORKS (ex. 1): Get all property names by category_id.",
    response_model=ResultListOut,
)
async def get_product_properties_from_db(
    category_id: int, session: AsyncSession = Depends(get_session)
):
    is_category_exist = await Category.is_category_id_exist(category_id=category_id)
    if not is_category_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="GATEGORY_ID_DOES_NOT_EXIST"
        )
    properties_sql_data = await session.execute(
        text(QUERY_TO_GET_PROPERTIES.format(category_id=category_id))
    )
    properties_raw_data = [dict(row) for row in properties_sql_data if row]
    if not properties_raw_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PROPERTIES_NOT_FOUND"
        )
    unique_property_names = list(set(row["name"] for row in properties_raw_data))
    json_result = [dict(key=name, values=[]) for name in unique_property_names]
    for row in properties_raw_data:
        for json_row in json_result:
            if json_row["key"] == row["name"]:
                json_row["values"].append(
                    dict(value=row["value"], optional_value=row["optional_value"])
                )
                break

    return JSONResponse(status_code=status.HTTP_200_OK, content={"result": json_result})


@suppliers.get(
    "/get_product_variations/{category_id}/",
    summary="WORKS (ex. 1): Get all variation names and values by category_id.",
    response_model=ResultListOut,
)
async def get_product_variations_from_db(
    category_id: int, session: AsyncSession = Depends(get_session)
):
    is_category_exist = await Category.is_category_id_exist(category_id=category_id)
    if not is_category_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="GATEGORY_ID_DOES_NOT_EXIST"
        )
    variations_sql_data = await session.execute(
        text(QUERY_TO_GET_VARIATIONS.format(category_id=category_id))
    )
    variations_raw_data = [dict(row) for row in variations_sql_data if row]
    if not variations_raw_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="VARIATIONS_NOT_FOUND"
        )
    json_variations: Dict[str, Any] = dict()
    for row in variations_raw_data:
        if row["name"] not in json_variations:
            json_variations[row["name"]] = list()
        json_variations[row["name"]].append(row["value"])

    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": json_variations}
    )


@suppliers.post(
    "/add_product/",
    summary="WORKS: Add product to database.",
    response_model=ProductIdOut,
)
async def add_product_info_to_db(
    product_info: ProductInfo,
    properties: List[PropertiesDict],
    variations: List[VariationsDict],
    prices: List[ProductPrices],
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    if not prices:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PRODUCT_PRICES_IS_EMPTY",
        )
    supplier_id = await Supplier.get_supplier_id_by_email(email=user_email)
    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT_SUPPLIER"
        )
    category_id = product_info.category_id
    is_category_id_exist = await Category.is_category_id_exist(category_id=category_id)
    if not is_category_id_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="GATEGORY_ID_DOES_NOT_EXIST"
        )
    current_datetime = utils.get_moscow_datetime()
    product = Product(
        supplier_id=supplier_id,
        category_id=category_id,
        name=product_info.product_name,
        description=product_info.description,
        datetime=current_datetime,
        UUID="",
    )
    session.add(product)
    await session.commit()

    try:
        product_id = await session.execute(
            select(func.max(Product.id)).where(
                and_(
                    Product.supplier_id.__eq__(supplier_id),
                    Product.name.__eq__(product_info.product_name),
                )
            )
        )
        product_id = product_id.scalar()

        all_cpv_id = list()  # used in 'except' blok
        for property in properties:
            category_property_type_id = await session.execute(
                select(CategoryPropertyType.id).where(
                    CategoryPropertyType.name.__eq__(property.name)
                )
            )
            category_property_type_id = category_property_type_id.scalar()
            if not category_property_type_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=dict(error="PROPERTY_NOT_FOUND", name=property.name),
                )
            is_property_match_category = await session.execute(
                select(CategoryProperty.id).where(
                    and_(
                        CategoryProperty.category_id.__eq__(category_id),
                        CategoryProperty.property_type_id.__eq__(
                            category_property_type_id
                        ),
                    )
                )
            )
            is_property_match_category = bool(is_property_match_category.scalar())
            if not is_property_match_category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=dict(
                        error="PROPERTY_DOES_NOT_MATCH_CATEGORY", name=property.name
                    ),
                )
            category_property_value_id = (
                await CategoryPropertyValue.get_category_property_value_id(
                    category_property_type_id=category_property_type_id,
                    value=property.value,
                    optional_value=property.optional_value,
                )
            )
            if not category_property_value_id:
                category_property_value = CategoryPropertyValue(
                    property_type_id=category_property_type_id,
                    value=property.value,
                    optional_value=property.optional_value,
                )
                session.add(category_property_value)
                await session.commit()

                category_property_value_id = (
                    await CategoryPropertyValue.get_category_property_value_id(
                        category_property_type_id=category_property_type_id,
                        value=property.value,
                        optional_value=property.optional_value,
                    )
                )
                all_cpv_id.append(category_property_value_id)
            product_property_value = ProductPropertyValue(
                product_id=product_id, property_value_id=category_property_value_id
            )
            session.add(product_property_value)

        all_pvv_id_parent = list()  # used in 'except' blok
        for variation in variations:
            category_variation_type_id = await session.execute(
                select(CategoryVariation.variation_type_id)
                .join(CategoryVariationType)
                .where(
                    and_(
                        CategoryVariationType.name.__eq__(variation.name),
                        CategoryVariation.category_id.__eq__(category_id),
                    )
                )
            )
            category_variation_type_id = category_variation_type_id.scalar()
            if not category_variation_type_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=dict(
                        error="VARIATION_NAME_DOES_NOT_EXIST", name=variation.name
                    ),
                )
            category_variation_value_id = (
                await CategoryVariationValue.get_category_variation_value_id(
                    category_variation_type_id=category_variation_type_id,
                    value=variation.value,
                )
            )
            if not category_variation_value_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=dict(
                        error="VARIATION_VALUE_DOES_NOT_EXIST", value=variation.value
                    ),
                )
            product_variation_value_id_parent = (
                await ProductVariationValue.get_product_variation_value_id(
                    product_id=product_id,
                    category_variation_value_id=category_variation_value_id,
                )
            )
            if not product_variation_value_id_parent:
                product_variation_value = ProductVariationValue(
                    product_id=product_id,
                    variation_value_id=category_variation_value_id,
                )
                session.add(product_variation_value)
                await session.commit()
                product_variation_value_id_parent = (
                    await ProductVariationValue.get_product_variation_value_id(
                        product_id=product_id,
                        category_variation_value_id=category_variation_value_id,
                    )
                )
            all_pvv_id_parent.append(product_variation_value_id_parent)
            if not variation.childs:
                if not variation.count:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=dict(
                            error="COUNT_IS_NOT_PROVIDED", value=variation.value
                        ),
                    )
                product_variations_count = ProductVariationCount(
                    product_variation_value1_id=product_variation_value_id_parent,
                    count=variation.count,
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
                                    child_variation=child_variation.value,
                                ),
                            ),
                        )
                    category_variation_type_id = await session.execute(
                        select(CategoryVariation.variation_type_id)
                        .join(CategoryVariationType)
                        .where(
                            and_(
                                CategoryVariationType.name.__eq__(child_variation.name),
                                CategoryVariation.category_id.__eq__(category_id),
                            )
                        )
                    )
                    category_variation_type_id = category_variation_type_id.scalar()
                    if not category_variation_type_id:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=dict(
                                error="VARIATION_NAME_DOES_NOT_EXIST",
                                name=child_variation.name,
                            ),
                        )
                    category_variation_value_id = (
                        await CategoryVariationValue.get_category_variation_value_id(
                            category_variation_type_id=category_variation_type_id,
                            value=child_variation.value,
                        )
                    )
                    if not category_variation_value_id:
                        raise HTTPException(
                            status_code=status.HTTP_404_NOT_FOUND,
                            detail=dict(
                                error="VARIATION_VALUE_DOES_NOT_EXIST",
                                value=child_variation.value,
                            ),
                        )
                    product_variation_value_id_child = (
                        await ProductVariationValue.get_product_variation_value_id(
                            product_id=product_id,
                            category_variation_value_id=category_variation_value_id,
                        )
                    )
                    if not product_variation_value_id_child:
                        product_variation_value = ProductVariationValue(
                            product_id=product_id,
                            variation_value_id=category_variation_value_id,
                        )
                        session.add(product_variation_value)
                        await session.commit()

                        product_variation_value_id_child = (
                            await ProductVariationValue.get_product_variation_value_id(
                                product_id=product_id,
                                category_variation_value_id=category_variation_value_id,
                            )
                        )
                    product_variations_count = ProductVariationCount(
                        product_variation_value1_id=product_variation_value_id_parent,
                        product_variation_value2_id=product_variation_value_id_child,
                        count=child_variation.count,
                    )
                    session.add(product_variations_count)

        product_price_all_quantities = [price.quantity for price in prices]
        if len(product_price_all_quantities) != len(set(product_price_all_quantities)):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="NOT_UNIQUE_QUANTITIES_PROVIDED",
            )
        for price in prices:
            product_price = ProductPrice(
                product_id=product_id, value=price.value, min_quantity=price.quantity
            )
            session.add(product_price)
        await session.commit()

        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"product_id": product_id}
        )

    except Exception as error:
        if "product_variation_value_id_parent" in locals():
            for pvv_id_parent in all_pvv_id_parent:
                await session.execute(
                    delete(ProductVariationCount).where(
                        ProductVariationCount.product_variation_value1_id.__eq__(
                            pvv_id_parent
                        )
                    )
                )
        if "product_id" in locals():
            await session.execute(
                delete(ProductVariationValue).where(
                    ProductVariationValue.product_id.__eq__(product_id)
                )
            )
            await session.execute(
                delete(ProductPropertyValue).where(
                    ProductPropertyValue.product_id.__eq__(product_id)
                )
            )
        if "category_property_type_id" in locals():
            for cpt_id in all_cpv_id:
                await session.execute(
                    delete(CategoryPropertyValue).where(
                        CategoryPropertyValue.id.__eq__(cpt_id)
                    )
                )
        if "product_id" in locals():
            await session.execute(
                delete(ProductPrice).where(ProductPrice.product_id.__eq__(product_id))
            )
            await session.execute(delete(Product).where(Product.id.__eq__(product_id)))
        await session.commit()
        raise error


@suppliers.get(
    "/manage_products/",
    summary="WORKS: Get list of all suppliers products.",
    response_model=ProductIdOut,
)
async def get_supplier_products(
    Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    supplier_id = await Supplier.get_supplier_id_by_email(email=user_email)
    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT_SUPPLIER"
        )
    products = await session.execute(
        text(QUERY_SUPPLIER_PRODUCTS.format(supplier_id=supplier_id))
    )
    products = [dict(row) for row in products]
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="PRODUCTS_NOT_FOUND"
        )
    return JSONResponse(status_code=status.HTTP_200_OK, content={"result": products})


@suppliers.patch(
    "/delete_products/",
    summary="WORKS: Delete products (change is_active to 0).",
    response_model=ProductIdOut,
)
async def delete_supplier_products(
    products: List[int],
    product_list_in_output: bool = True,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    supplier_id = await Supplier.get_supplier_id_by_email(email=user_email)
    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT_SUPPLIER"
        )
    for product_id in products:
        is_product_match_supplier = await Product.is_product_match_supplier(
            product_id=product_id, supplier_id=supplier_id
        )
        if not is_product_match_supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=dict(
                    error="PRODUCT_DOES_NOT_BELONG_SUPPLIER", product_id=product_id
                ),
            )
        await session.execute(
            update(Product).where(Product.id.__eq__(product_id)).values(is_active=0)
        )
    await session.commit()

    if product_list_in_output:
        products = await session.execute(
            text(QUERY_SUPPLIER_PRODUCTS.format(supplier_id=supplier_id))
        )
        products = [dict(row) for row in products]
        if not products:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="PRODUCTS_NOT_FOUND"
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"result": products}
        )
    else:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"result": "OK"})


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

    _, file_extension = os.path.splitext(file.filename)

    contents = await file.read()
    await file.seek(0)

    # file validation
    if not utils.is_image(contents=contents):
        logging.error("File is not an image: '%s'", file.filename)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_IMAGE")

    new_file_url = await utils.upload_file_to_s3(
        bucket=AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
        file=utils.Dict(file=file.file, extension=file_extension),
        contents=contents,
    )

    # Upload data to DB
    product_image = await session.execute(
        select(ProductImage).where(
            and_(
                ProductImage.product_id == product_id,
                ProductImage.serial_number == serial_number,
            )
        )
    )
    product_image = product_image.scalar()

    if not product_image:
        await session.execute(
            insert(ProductImage).values(
                product_id=product_id,
                image_url=new_file_url,
                serial_number=serial_number,
            )
        )

        logging.info(
            "Image for product_id '%s' is added to DB: image_url='%s', serial_number='%s'",
            product_id,
            new_file_url,
            serial_number,
        )
    elif not product_image.image_url == new_file_url:
        # looking for the same images in db
        same_images = await session.execute(
            select(ProductImage).where(
                ProductImage.image_url.__eq__(product_image.image_url)
            )
        )
        same_images = same_images.all()

        # remove the file from s3 if it doesn't have any reference in db
        if len(same_images) == 1:
            files_to_remove = [
                utils.Dict(
                    bucket=AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
                    key=product_image.image_url.split(".com/")[-1],
                )
            ]
            await utils.remove_files_from_s3(files=files_to_remove)

        # update db
        await session.execute(
            update(ProductImage)
            .where(
                and_(
                    ProductImage.product_id == product_id,
                    ProductImage.serial_number == serial_number,
                )
            )
            .values(image_url=new_file_url)
        )

        logging.info(
            "Image for product_id '%s' is updated in DB: image_url='%s', serial_number='%s'",
            product_id,
            new_file_url,
            serial_number,
        )

    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "IMAGE_LOADED_SUCCESSFULLY"},
    )


@suppliers.delete(
    "/delete_product_image/",
    summary="WORKS: Delete provided product image from AWS S3 and url from DB",
)
async def delete_product_image(
    product_id: int,
    serial_number: int,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    supplier_id = await Supplier.get_supplier_id_by_email(email=user_email)
    product_image = await session.execute(
        select(ProductImage)
        .select_from(Product)
        .where(
            and_(
                Product.id.__eq__(product_id),
                Product.supplier_id.__eq__(supplier_id),
            )
        )
        .join(ProductImage)
        .where(ProductImage.serial_number.__eq__(serial_number))
    )
    product_image = product_image.scalar()

    if not product_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )

    # looking for the same images in db
    same_images = await session.execute(
        select(ProductImage).where(
            ProductImage.image_url.__eq__(product_image.image_url)
        )
    )
    same_images = same_images.all()

    # remove the file from s3 if it doesn't have any reference in db
    if len(same_images) == 1:
        files_to_remove = [
            utils.Dict(
                bucket=AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
                key=product_image.image_url.split(".com/")[-1],
            )
        ]
        await utils.remove_files_from_s3(files=files_to_remove)

    # remove the image row from db
    await session.delete(product_image)
    await session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "IMAGE_DELETED_SUCCESSFULLY"},
    )


@suppliers.get(
    "/company_info/",
    summary="WORKS: Get company info (name, logo_url) by token.",
    response_model=CompanyInfo,
)
async def get_supplier_company_info(
    Authorize: AuthJWT = Depends(), session: AsyncSession = Depends(get_session)
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    supplier_id = await Supplier.get_supplier_id_by_email(email=user_email)
    if not supplier_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT_SUPPLIER"
        )
    company_info = await session.execute(
        select(Company.name, Company.logo_url).where(
            Company.supplier_id.__eq__(supplier_id)
        )
    )
    result = None
    for row in company_info:
        result = dict(row)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="COMPANY_NOT_FOUND"
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": result},
    )


@suppliers.post(
    "/upload_company_image/",
    summary="WORKS: Uploads provided company image to AWS S3 and saves url to DB",
)
async def upload_company_image(
    file: UploadFile,
    serial_number: int,
    authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    authorize.jwt_required()
    user_email = json.loads(authorize.get_jwt_subject())["email"]
    company_id = await session.execute(
        select(Company.id)
        .select_from(User)
        .where(User.email.__eq__(user_email))
        .join(Supplier, User.id.__eq__(Supplier.user_id))
        .join(Company, Supplier.id.__eq__(Company.supplier_id))
    )
    company_id = company_id.scalar()

    _, file_extension = os.path.splitext(file.filename)

    contents = await file.read()
    await file.seek(0)

    # file validation
    if not utils.is_image(contents=contents):
        logging.error("File is not an image: '%s'", file.filename)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT_IMAGE")

    new_file_url = await utils.upload_file_to_s3(
        bucket=AWS_S3_COMPANY_IMAGES_BUCKET,
        file=utils.Dict(file=file.file, extension=file_extension),
        contents=contents,
    )

    # get company image by serial number
    company_image = await session.execute(
        select(CompanyImages).where(
            and_(
                CompanyImages.company_id == company_id,
                CompanyImages.serial_number == serial_number,
            )
        )
    )
    company_image = company_image.scalar()

    if not company_image:
        await session.execute(
            insert(CompanyImages).values(
                company_id=company_id,
                url=new_file_url,
                serial_number=serial_number,
            )
        )

        logging.info(
            "Image for company_id '%s' is added to DB: image_url='%s', serial_number='%s'",
            company_id,
            new_file_url,
            serial_number,
        )
    elif not company_image.url == new_file_url:
        # looking for the same images in db
        same_images = await session.execute(
            select(CompanyImages).where(CompanyImages.url.__eq__(company_image.url))
        )
        same_images = same_images.all()

        # remove the file from s3 if it doesn't have any reference in db
        if len(same_images) == 1:
            files_to_remove = [
                utils.Dict(
                    bucket=AWS_S3_COMPANY_IMAGES_BUCKET,
                    key=company_image.url.split(".com/")[-1],
                )
            ]
            await utils.remove_files_from_s3(files=files_to_remove)

        # update db
        await session.execute(
            update(CompanyImages)
            .where(
                and_(
                    CompanyImages.company_id == company_id,
                    CompanyImages.serial_number == serial_number,
                )
            )
            .values(url=new_file_url)
        )

        logging.info(
            "Image for company_id '%s' is updated in DB: image_url='%s', serial_number='%s'",
            company_id,
            new_file_url,
            serial_number,
        )

    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "IMAGE_LOADED_SUCCESSFULLY"},
    )


@suppliers.delete(
    "/delete_company_image/",
    summary="WORKS: Delete provided company image from AWS S3 and url from DB",
)
async def delete_company_image(
    company_id: int,
    serial_number: int,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    supplier_id = await Supplier.get_supplier_id_by_email(email=user_email)
    company_image = await session.execute(
        select(CompanyImages)
        .select_from(Company)
        .where(
            and_(
                Company.id.__eq__(company_id),
                Company.supplier_id.__eq__(supplier_id),
            )
        )
        .join(CompanyImages)
        .where(CompanyImages.serial_number.__eq__(serial_number))
    )
    company_image = company_image.scalar()

    if not company_image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Image not found"
        )

    # looking for the same image references in db
    same_images = await session.execute(
        select(CompanyImages).where(CompanyImages.url.__eq__(company_image.url))
    )
    same_images = same_images.all()

    # remove the file from s3 if it doesn't have any reference in db
    if len(same_images) == 1:
        files_to_remove = [
            utils.Dict(
                bucket=AWS_S3_COMPANY_IMAGES_BUCKET,
                key=company_image.url.split(".com/")[-1],
            )
        ]
        await utils.remove_files_from_s3(files=files_to_remove)

    # remove the image row from db
    await session.delete(company_image)
    await session.commit()

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"result": "IMAGE_DELETED_SUCCESSFULLY"},
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
