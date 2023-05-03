from datetime import datetime
from typing import List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path, Query
from sqlalchemy import and_, join
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.app import aws_s3, crud
from core.depends import Authorization, DatabaseSession, Image
from core.settings import aws_s3_settings
from orm import (
    CategoryPropertyModel,
    CategoryPropertyValueModel,
    CategoryVariationModel,
    CategoryVariationTypeModel,
    CategoryVariationValueModel,
    CompanyImageModel,
    CompanyModel,
    ProductImageModel,
    ProductModel,
    ProductPriceModel,
    ProductPropertyValueModel,
    ProductVariationValueModel,
    SupplierModel,
    UserModel,
)
from schemas import (
    ApplicationResponse,
    BodyCompanyDataRequest,
    BodyProductUploadRequest,
    BodySupplierDataRequest,
    BodyUserDataRequest,
    CategoryPropertyValue,
    CategoryVariationValue,
    Company,
    CompanyImage,
    Product,
    ProductImage,
    QueryPaginationRequest,
    Supplier,
)
from typing_ import RouteReturnT


async def supplier_required(user: Authorization) -> None:
    if not user.supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found",
        )


router = APIRouter(dependencies=[Depends(supplier_required)])


@router.get(
    path="/getSupplierInfo/",
    deprecated=True,
    description="Moved to /login/current/",
    summary="WORKS: Get supplier info (personal and business).",
    response_model=ApplicationResponse[Supplier],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def get_supplier_data_info(user: Authorization) -> RouteReturnT:
    return {
        "ok": True,
        "result": user.supplier,
    }


async def send_account_info_core(
    session: AsyncSession,
    user_id: int,
    supplier_id: int,
    company_exits: bool,
    user_data_request: BodyUserDataRequest,
    supplier_data_request: BodySupplierDataRequest,
    company_data_request: BodyCompanyDataRequest,
) -> None:
    await crud.users.update.one(
        session=session, values=user_data_request.dict(), where=UserModel.id == user_id
    )
    await crud.suppliers.update.one(
        session=session, values=supplier_data_request.dict(), where=SupplierModel.id == supplier_id
    )

    if company_exits:
        await crud.companies.update.one(
            session=session,
            values=company_data_request.dict(),
            where=CompanyModel.supplier_id == supplier_id,
        )
    else:
        await crud.companies.insert.one(
            session=session,
            values={
                CompanyModel.supplier_id: supplier_id,
                **company_data_request.dict(),
            },
        )


@router.post(
    path="/sendAccountInfo/",
    summary="WORKS: Should be discussed. 'images_url' insert images in company_images, other parameters update corresponding values.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def send_account_info(
    user: Authorization,
    session: DatabaseSession,
    user_data_request: BodyUserDataRequest = Body(...),
    supplier_data_request: BodySupplierDataRequest = Body(...),
    company_data_request: BodyCompanyDataRequest = Body(...),
) -> RouteReturnT:
    await send_account_info_core(
        session=session,
        user_id=user.id,
        supplier_id=user.supplier.id,
        company_exits=bool(user.supplier.company),
        user_data_request=user_data_request,
        supplier_data_request=supplier_data_request,
        company_data_request=company_data_request,
    )

    return {
        "ok": True,
        "result": True,
    }


async def get_product_properties_core(
    session: AsyncSession, category_id: int
) -> List[CategoryPropertyValue]:
    return await crud.categories_property_values.get.many(
        session=session,
        where=[CategoryPropertyModel.category_id == category_id],
        select_from=[
            join(
                CategoryPropertyValueModel,
                CategoryPropertyModel,
                CategoryPropertyValueModel.property_type_id
                == CategoryPropertyModel.property_type_id,
            )
        ],
    )


@router.get(
    path="/getCategoryProperties/{category_id}/",
    summary="WORKS: Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[CategoryPropertyValue]],
    status_code=status.HTTP_200_OK,
)
async def get_product_properties(
    session: DatabaseSession,
    category_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_product_properties_core(session=session, category_id=category_id),
    }


async def get_product_variations_core(
    session: AsyncSession, category_id: int
) -> List[CategoryVariationValue]:
    return await crud.categories_variation_values.get.many(
        session=session,
        where=[CategoryVariationModel.category_id == category_id],
        options=[
            selectinload(CategoryVariationValueModel.type),
        ],
        select_from=[
            join(
                CategoryVariationModel,
                CategoryVariationTypeModel,
                CategoryVariationModel.variation_type_id == CategoryVariationTypeModel.id,
            )
        ],
    )


@router.get(
    path="/getCategoryVariations/{category_id}/",
    summary="WORKS (ex. 1): Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[CategoryVariationValue]],
    status_code=status.HTTP_200_OK,
)
async def get_product_variations(
    session: DatabaseSession,
    category_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_product_variations_core(session=session, category_id=category_id),
    }


async def add_product_info_core(
    request: BodyProductUploadRequest,
    supplier_id: int,
    session: AsyncSession,
) -> ProductModel:
    product = await crud.products.insert.one(
        session=session,
        values={
            ProductModel.supplier_id: supplier_id,
            ProductModel.description: request.description,
            ProductModel.datetime: datetime.now(),
            ProductModel.name: request.name,
            ProductModel.category_id: request.category_id,
        },
    )
    if request.properties:
        await crud.products_property_values.insert.many(
            session=session,
            values=[
                {
                    ProductPropertyValueModel.product_id: product.id,
                    ProductPropertyValueModel.property_value_id: property_value_id,
                }
                for property_value_id in request.properties
            ],
        )
    if request.variations:
        await crud.products_variation_values.insert.many(
            session=session,
            values=[
                {
                    ProductVariationValueModel.product_id: product.id,
                    ProductVariationValueModel.variation_value_id: variation_value_id,
                }
                for variation_value_id in request.variations
            ],
        )

    await crud.products_prices.insert.many(
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
    path="/addProduct/",
    summary="WORKS: Add product to database.",
    response_model=ApplicationResponse[Product],
    status_code=status.HTTP_200_OK,
)
async def add_product_info(
    user: Authorization,
    session: DatabaseSession,
    request: BodyProductUploadRequest = Body(...),
) -> RouteReturnT:
    product = await add_product_info_core(
        request=request, supplier_id=user.supplier.id, session=session
    )

    return {
        "ok": True,
        "result": product,
    }


async def manage_products_core(
    session: AsyncSession,
    supplier_id: int,
    offset: int,
    limit: int,
) -> List[ProductModel]:
    return await crud.products.get.many(
        session=session,
        where=[ProductModel.supplier_id == supplier_id],
        options=[selectinload(ProductModel.prices)],
        offset=offset,
        limit=limit,
    )


@router.get(
    path="/manageProducts/",
    summary="WORKS: Get list of all suppliers products.",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_200_OK,
)
async def manage_products(
    user: Authorization,
    session: DatabaseSession,
    pagination: QueryPaginationRequest = Depends(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await manage_products_core(
            session=session,
            supplier_id=user.supplier.id,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
    }


async def delete_products_core(
    session: AsyncSession, supplier_id: int, products: List[int]
) -> None:
    await crud.products.update.many(
        session=session,
        values={
            ProductModel.is_active: 0,
        },
        where=and_(ProductModel.id.in_(products), ProductModel.supplier_id == supplier_id),
    )


@router.patch(
    path="/deleteProducts/",
    summary="WORKS: Delete products (change is_active to 0).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_products(
    user: Authorization,
    session: DatabaseSession,
    products: List[int] = Body(...),
) -> RouteReturnT:
    await delete_products_core(
        session=session,
        supplier_id=user.supplier.id,
        products=products,
    )

    return {
        "ok": True,
        "result": True,
    }


@router.post(
    path="/uploadProductImage/",
    summary="WORKS: Uploads provided product image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[ProductImage],
    status_code=status.HTTP_200_OK,
)
async def upload_product_image(
    file: Image,
    session: DatabaseSession,
    product_id: int = Query(...),
    order: int = Query(...),
) -> RouteReturnT:
    link = await aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET, file=file
    )

    product_image = await crud.products_images.insert.one(
        session=session,
        values={
            ProductImageModel.image_url: link,
            ProductImageModel.product_id: product_id,
            ProductImageModel.order: order,
        },
    )

    return {
        "ok": True,
        "result": product_image,
    }


@router.delete(
    path="/deleteProductImage/",
    summary="WORKS: Delete provided product image from AWS S3 and url from DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_product_image(
    session: DatabaseSession,
    product_id: int = Query(...),
    order: int = Query(...),
) -> RouteReturnT:
    image = await crud.products_images.delete.one(
        session=session,
        where=and_(
            ProductImageModel.product_id == product_id,
            ProductImageModel.order == order,
        ),
    )

    await aws_s3.delete_file_from_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
        url=image.image_url,
    )

    return {
        "ok": True,
        "result": True,
    }


@router.get(
    path="/companyInfo/",
    summary="WORKS: Get company info (name, logo_url) by token.",
    response_model=ApplicationResponse[Company],
    status_code=status.HTTP_200_OK,
)
async def get_supplier_company_info(user: Authorization) -> RouteReturnT:
    return {
        "ok": True,
        "result": user.supplier.company,
    }


@router.post(
    path="/uploadCompanyImage/",
    summary="WORKS: Uploads provided company image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[CompanyImage],
    status_code=status.HTTP_200_OK,
)
async def upload_company_image(
    file: Image,
    user: Authorization,
    session: DatabaseSession,
) -> RouteReturnT:
    link = await aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET, file=file
    )

    company_image = await crud.companies_images.insert.one(
        session=session,
        values={
            CompanyImageModel.company_id: user.supplier.company.id,
            CompanyImageModel.url: link,
        },
    )

    return {
        "ok": True,
        "result": company_image,
    }


@router.delete(
    path="/deleteCompanyImage/",
    summary="WORKS: Delete provided company image from AWS S3 and url from DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_company_image(
    user: Authorization,
    session: DatabaseSession,
) -> RouteReturnT:
    company = await crud.companies.get.one(
        session=session,
        where=[CompanyModel.supplier_id == user.supplier.id],
    )
    image = await crud.companies_images.delete.one(
        session=session,
        where=CompanyImageModel.company_id == company.id,
    )

    await aws_s3.delete_file_from_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET, url=image.url
    )

    return {
        "ok": True,
        "result": True,
    }
