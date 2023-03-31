import imghdr
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import APIRouter, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Query
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import join, joinedload
from starlette import status

from core.depends import (
    FileObjects,
    UserObjects,
    auth_required,
    get_session,
    image_required,
)
from core.settings import aws_s3_settings
from core.tools import store
from orm import (
    CategoryModel,
    CompanyImageModel,
    CompanyModel,
    ProductImageModel,
    ProductModel,
    ProductPriceModel,
    ProductPropertyValueModel,
    ProductVariationValueModel,
)
from schemas import (
    ApplicationResponse,
    BodyProductUploadRequest,
    CategoryPropertyType,
    CategoryPropertyValue,
    CategoryVariationType,
    CategoryVariationValue,
    Company,
    CompanyImage,
    Product,
    ProductImage,
    SuppliersProductsResponse,
)


async def supplier_required(user: UserObjects = Depends(auth_required)) -> None:
    if not user.orm.supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found",
        )


router = APIRouter(dependencies=[Depends(supplier_required)])


async def upload_file_to_s3(file: FileObjects) -> str:
    return await store.aws_s3.upload(
        bucket_name=aws_s3_settings.AWS_S3_COMPANY_IMAGES_BUCKET,
        file_data={"extension": Path(file.source.filename).suffix},
        contents=file.contents,
        file=file.source,
    )


async def add_product_info_core(
    request: BodyProductUploadRequest,
    supplier_id: int,
    session: AsyncSession,
) -> ProductModel:
    product = await store.orm.products.insert_one(
        session=session,
        values={
            ProductModel.supplier_id: supplier_id,
            ProductModel.description: request.description,
            ProductModel.datetime: datetime.now(),
            ProductModel.name: request.name,
            ProductModel.category_id: request.category_id,
        },
    )
    if request.property_ids:
        await store.orm.products_property_values.insert_many(
            session=session,
            values=[
                {
                    ProductPropertyValueModel.product_id: product.id,
                    ProductPropertyValueModel.property_value_id: property_value_id,
                }
                for property_value_id in request.property_ids
            ],
        )
    if request.varitaion_ids:
        await store.orm.products_variation_values.insert_many(
            session=session,
            values=[
                {
                    ProductVariationValueModel.product_id: product.id,
                    ProductVariationValueModel.variation_value_id: variation_value_id,
                }
                for variation_value_id in request.varitaion_ids
            ],
        )

    await store.orm.products_prices.insert_many(
        session=session,
        values=[
            {
                ProductPriceModel.product_id: product.id,
                ProductPriceModel.discount: price.discount,
                ProductPriceModel.value: price.value,
                ProductPriceModel.min_quantity: price.min_quantity,
                ProductPriceModel.start_date: price.start_date,
                ProductPriceModel.end_date: price.end_date,
            }
            for price in request.prices
        ],
    )

    return product


@router.post(
    path="/addProduct",
    summary="WORKS: Add product to database.",
    response_model=ApplicationResponse[Product],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/add_product/",
    description="Moved to /suppliers/addProduct",
    deprecated=True,
    summary="WORKS: Add product to database.",
    response_model=ApplicationResponse[Product],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def add_product_info(
    request: BodyProductUploadRequest = Body(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[Product]:
    product = await add_product_info_core(
        request=request, supplier_id=user.schema.supplier.id, session=session
    )

    return {
        "ok": True,
        "result": product,
    }


@router.get(
    path="/companyInfo",
    summary="WORKS: Get company info (name, logo_url) by token.",
    response_model=ApplicationResponse[Company],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/company_info",
    description="Moved to /suppliers/companyInfo",
    deprecated=True,
    summary="WORKS: Get company info (name, logo_url) by token.",
    response_model=ApplicationResponse[Company],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_supplier_company_info(
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[Company]:
    company = await store.orm.companies.get_one(
        session=session, where=[CompanyModel.supplier_id == user.schema.supplier.id]
    )

    return {"ok": True, "result": company}


@router.post(
    path="/uploadCompanyImage",
    summary="WORKS: Uploads provided company image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[CompanyImage],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/upload_company_image",
    description="Moved to /suppliers/uploadCompanyImage",
    deprecated=True,
    summary="WORKS: Uploads provided company image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[CompanyImage],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def upload_company_image(
    file: FileObjects = Depends(image_required),
    order: int = Query(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[CompanyImage]:
    company = await store.orm.companies.get_one(
        session=session, where=[CompanyModel.supplier_id == user.schema.supplier.id]
    )

    link = await upload_file_to_s3(file=file)

    company_image = await store.orm.companies_images.insert_one(
        session=session,
        values={
            CompanyImageModel.company_id: company.id,
            CompanyImageModel.url: link,
            CompanyImageModel.order: order,
        },
    )

    return {
        "ok": True,
        "result": company_image,
    }


@router.delete(
    path="/deleteCompanyImage",
    summary="WORKS: Delete provided company image from AWS S3 and url from DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.delete(
    path="/delete_company_image",
    description="Moved to /suppliers/deleteCompanyImage",
    deprecated=True,
    summary="WORKS: Delete provided company image from AWS S3 and url from DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def delete_company_image(
    order: int = Query(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[bool]:
    company = await store.orm.companies.get_one(
        session=session, where=[CompanyModel.supplier_id == user.schema.supplier.id]
    )
    deleted_image = await store.orm.companies_images.delete_one(
        session=session,
        where=and_(
            CompanyImageModel.company_id == company.id,
            CompanyImageModel.order == order,
        ),
    )

    key_to_delete = ["/".join(deleted_image.url.split("/")[-2:])]
    await store.aws_s3.remove(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
        files_to_delete=key_to_delete,
    )

    return {
        "ok": True,
        "result": True,
    }


@router.post(
    path="/uploadProductImage",
    summary="WORKS: Uploads provided product image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[ProductImage],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/upload_product_image",
    description="Moved to /suppliers/uploadProductImage",
    deprecated=True,
    summary="WORKS: Uploads provided product image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[ProductImage],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def upload_product_image(
    file: FileObjects = Depends(image_required),
    product_id: int = Query(...),
    order: int = Query(...),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[ProductImage]:
    link = await upload_file_to_s3(file=file)

    product_image = await store.orm.products_images.insert_one(
        session=session,
        values={
            ProductImageModel.image_url: link,
            ProductImageModel.product_id: product_id,
            ProductImageModel.order: order,
        },
    )

    return {"ok": True, "result": product_image}


@router.get(
    path="/getCategoryVariations/{category_id}",
    summary="WORKS (ex. 1): Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[CategoryVariationValue]],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/get_category_variations/{category_id}",
    description="Moved to /suppliers/getCategoryVariations/{category_id}",
    deprecated=True,
    summary="WORKS (ex. 1): Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[CategoryVariationValue]],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_product_variations(
    category_id: int = Path(...),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[CategoryVariationType]]:
    category = await store.orm.categories.get_one(
        session=session,
        where=[CategoryModel.id == category_id],
        options=[
            joinedload(CategoryModel.variations.values),
        ],
    )

    return {"ok": True, "result": category.variations}


@router.get(
    path="/getCategoryProperties/{category_id}",
    summary="WORKS: Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[CategoryPropertyType]],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/get_category_properties/{category_id}",
    description="Moved to /suppliers/getCategoryProperties/{category_id}",
    deprecated=True,
    summary="WORKS: Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[CategoryPropertyType]],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_product_properties(
    category_id: int = Path(...),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[CategoryPropertyType]]:
    category = await store.orm.categories.get_one(
        session=session,
        where=[CategoryModel.id == category_id],
        options=[joinedload(CategoryModel.properties)],
    )

    return {
        "ok": True,
        "result": category.properties,
    }
