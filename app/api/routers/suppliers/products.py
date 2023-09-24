from typing import List

from corecrud import (
    Join,
    Limit,
    Offset,
    Options,
    OrderBy,
    Returning,
    SelectFrom,
    Values,
    Where,
)
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from sqlalchemy import and_

from core.app import aws_s3, crud
from core.depends import DatabaseSession, Image, SupplierAuthorization
from core.settings import aws_s3_settings
from orm import (
    ProductImageModel,
    ProductModel,
    PropertyValueToProductModel,
    SupplierModel,
    VariationValueToProductModel,
    BundleModel,
    BundlableVariationValueModel,
)
from schemas import (
    ApplicationResponse,
    Product,
    ProductImage,
    ProductList,
)
from schemas.uploads import (
    PaginationUpload,
    ProductEditUpload,
    ProductSortingUpload,
    ProductUpload,
    SortFilterProductsUpload,
)
from typing_ import RouteReturnT

router = APIRouter()


async def add_product_info_core(
    request: ProductUpload,
    supplier_id: int,
    session: AsyncSession,
) -> ProductModel:
    product = await crud.products.insert.one(
        Values(
            {
                ProductModel.supplier_id: supplier_id,
                ProductModel.description: request.description,
                ProductModel.name: request.name,
                ProductModel.category_id: request.category_id,
            }
        ),
        Returning(ProductModel),
        session=session,
    )

    # bundle = await crud.bundles.insert.one( 
    #     Values( 
    #         {  
    #             BundleModel.product_id: product.id, 
    #             BundleModel.stock: request.stock,
    #         }
    #     ),
    #     Returning(BundleModel), 
    #     session=session,
    # )

    # bundlable_variations = await crud.bundlable_variations_values.insert.many( 
    #     Values( 
    #         [
    #             { 
    #                 BundlableVariationValueModel.bundle_id: bundle.id, 
    #                 BundlableVariationValueModel.variation_value_id: bundle_variation_value.variation_value_id, 
    #                 BundlableVariationValueModel.amount: bundle_variation_value.amount, 
    #                 BundlableVariationValueModel.variation_type_id: bundle_variation_value.variation_type_id, 
    #                 BundlableVariationValueModel.product_id: product.id,
    #             }
    #             for bundle_variation_value in request.bundlable_variation_values
    #         ]
    #     ),
    #     Returning(BundlableVariationValueModel),
    #     session=session
    # )

    if request.properties:
        await crud.property_values_to_products.insert.many(
            Values(
                [
                    {
                        PropertyValueToProductModel.product_id: product.id,
                        PropertyValueToProductModel.property_value_id: property_value_id,
                    }
                    for property_value_id in request.properties
                ]
            ),
            Returning(PropertyValueToProductModel.id),
            session=session,
        )
    if request.variations:
        await crud.variation_values_to_products.insert.many(
            Values(
                [
                    {
                        VariationValueToProductModel.product_id: product.id,
                        VariationValueToProductModel.variation_value_id: variation_value_id,
                    }
                    for variation_value_id in request.variations
                ]
            ),
            Returning(VariationValueToProductModel.id),
            session=session,
        )

    await crud.products_prices.insert.many(
        Values(
            [
                {
                    ProductPriceModel.product_id: product.id,
                }
                | price.dict()
                for price in request.prices
            ],
        ),
        Returning(ProductPriceModel.id),
        session=session,
    )

    return product


@router.post(
    path="/add",
    summary="WORKS: Add product to database.",
    response_model=ApplicationResponse[Product],
    status_code=status.HTTP_200_OK,
)
async def add_product_info(
    user: SupplierAuthorization,
    session: DatabaseSession,
    request: ProductUpload = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await add_product_info_core(
            request=request, supplier_id=user.supplier.id, session=session
        ),
    }


async def edit_product_info_core(
    request: ProductEditUpload,
    product_id: int,
    supplier_id: int,
    session: AsyncSession,
) -> ProductModel:
    product = await crud.products.update.one(
        Where(
            ProductModel.id == product_id,
            ProductModel.supplier_id == supplier_id,
        ),
        Values(
            {
                ProductModel.name: request.name,
                ProductModel.description: request.description,
                ProductModel.category_id: request.category_id,
            }
        ),
        Returning(ProductModel),
        session=session,
    )
    if request.properties:
        await crud.property_values_to_products.insert.many(
            Values(
                [
                    {
                        PropertyValueToProductModel.product_id: product.id,
                        PropertyValueToProductModel.property_value_id: property_value_id,
                    }
                    for property_value_id in request.properties
                ]
            ),
            Returning(PropertyValueToProductModel.id),
            session=session,
        )
    if request.variations:
        await crud.variation_values_to_products.insert.many(
            Values(
                [
                    {
                        VariationValueToProductModel.product_id: product.id,
                        VariationValueToProductModel.variation_value_id: variation_value_id,
                    }
                    for variation_value_id in request.variations
                ]
            ),
            Returning(VariationValueToProductModel.id),
            session=session,
        )

    if request.prices:
        await crud.products_prices.insert.many(
            Values(
                [
                    {
                        ProductPriceModel.product_id: product.id,
                    }
                    | price.dict()
                    for price in request.prices
                ],
            ),
            Returning(ProductPriceModel.id),
            session=session,
        )

    return product


@router.put(
    path="/{product_id}/update",
    summary="WORKS: Edit product",
    response_model=ApplicationResponse[Product],
    status_code=status.HTTP_200_OK,
)
async def edit_product_info(
    user: SupplierAuthorization,
    session: DatabaseSession,
    product_id: int = Path(...),
    request: ProductEditUpload = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await edit_product_info_core(
            request=request, product_id=product_id, supplier_id=user.supplier.id, session=session
        ),
    }


async def restore_products_core(
    session: AsyncSession, supplier_id: int, products: List[int]
) -> None:
    await crud.products.update.many(
        Where(and_(ProductModel.id.in_(products), ProductModel.supplier_id == supplier_id)),
        Values(
            {
                ProductModel.is_active: True,
            }
        ),
        Returning(ProductModel.id),
        session=session,
    )


@router.post(
    path="/restore",
    summary="WORKS: Restore products (change is_active to True).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def restore_products(
    user: SupplierAuthorization,
    session: DatabaseSession,
    products: List[int] = Body(...),
) -> RouteReturnT:
    await restore_products_core(
        session=session,
        supplier_id=user.supplier.id,
        products=products,
    )

    return {
        "ok": True,
        "result": True,
    }


async def manage_products_core(
    session: AsyncSession,
    supplier_id: int,
    offset: int,
    limit: int,
    filters: SortFilterProductsUpload,
    sorting: ProductSortingUpload,
) -> ProductList:
    products = await crud.products.select.many(
        Where(
            ProductModel.supplier_id == supplier_id,
            ProductModel.category_id.in_(filters.category_ids) if filters.category_ids else True,
            ProductModel.is_active == filters.is_active if filters.is_active is not None else True,
            (ProductPriceModel.discount > 0)
            if filters.on_sale
            else (ProductPriceModel.discount == 0)
            if filters.on_sale is False
            else True,
        ),
        Join(ProductPriceModel, ProductPriceModel.product_id == ProductModel.id),
        Options(
            selectinload(ProductModel.prices),
            selectinload(ProductModel.supplier).joinedload(SupplierModel.company),
            selectinload(ProductModel.category),
        ),
        Offset(offset),
        Limit(limit),
        OrderBy(sorting.sort.by.asc() if sorting.ascending else sorting.sort.by.desc()),
        session=session,
    )

    products_data = await crud.raws.select.one(
        Where(
            ProductModel.supplier_id == supplier_id,
            ProductModel.category_id.in_(filters.category_ids) if filters.category_ids else True,
            ProductModel.is_active == filters.is_active if filters.is_active is not None else True,
            (ProductPriceModel.discount > 0)
            if filters.on_sale
            else (ProductPriceModel.discount == 0)
            if filters.on_sale is False
            else True,
        ),
        SelectFrom(ProductModel),
        Join(ProductPriceModel, ProductPriceModel.product_id == ProductModel.id),
        nested_select=[
            func.count(ProductModel.id).label("total_count"),
        ],
        session=session,
    )

    return {
        "total_count": products_data.total_count,
        "products": products,
    }


@router.post(
    path="/",
    summary="WORKS: Get list of all suppliers products.",
    response_model=ApplicationResponse[ProductList],
    status_code=status.HTTP_200_OK,
)
async def products(
    user: SupplierAuthorization,
    session: DatabaseSession,
    pagination: PaginationUpload = Depends(),
    filters: SortFilterProductsUpload = Body(...),
    sorting: ProductSortingUpload = Depends(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await manage_products_core(
            session=session,
            supplier_id=user.supplier.id,
            offset=pagination.offset,
            limit=pagination.limit,
            filters=filters,
            sorting=sorting,
        ),
    }


async def delete_products_core(
    session: AsyncSession, supplier_id: int, products: List[int]
) -> None:
    await crud.products.update.many(
        Where(and_(ProductModel.id.in_(products), ProductModel.supplier_id == supplier_id)),
        Values(
            {
                ProductModel.is_active: False,
            }
        ),
        Returning(ProductModel.id),
        session=session,
    )


@router.post(
    path="/delete",
    summary="WORKS: Delete products (change is_active to False).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_products(
    user: SupplierAuthorization,
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
    path="/images/upload",
    summary="WORKS: Uploads provided product image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[ProductImage],
    status_code=status.HTTP_200_OK,
)
async def upload_product_image(
    file: Image,
    user: SupplierAuthorization,
    session: DatabaseSession,
    product_id: int = Query(...),
    order: int = Query(...),
) -> RouteReturnT:
    link = await aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET, file=file
    )

    product = await crud.products.select.one(
        Where(
            and_(ProductModel.id == product_id, ProductModel.supplier_id == user.supplier.id),
        ),
        session=session,
    )
    if not product:
        raise HTTPException(
            detail="Product not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    product_image = await crud.products_images.select.one(
        Where(
            and_(
                ProductImageModel.product_id == product_id,
                ProductImageModel.order == order,
            )
        ),
        session=session,
    )
    if product_image:
        raise HTTPException(
            detail="Try another order",
            status_code=status.HTTP_409_CONFLICT,
        )

    product_image = await crud.products_images.insert.one(
        Values(
            {
                ProductImageModel.image_url: link,
                ProductImageModel.product_id: product_id,
                ProductImageModel.order: order,
            }
        ),
        Returning(ProductImageModel),
        session=session,
    )

    return {
        "ok": True,
        "result": product_image,
    }


@router.delete(
    path="/images/delete",
    summary="WORKS: Delete provided product image from AWS S3 and url from DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_product_image(
    session: DatabaseSession,
    product_id: int = Query(...),
    order: int = Query(...),
) -> RouteReturnT:
    image = await crud.products_images.delete.many(
        Where(
            and_(
                ProductImageModel.product_id == product_id,
                ProductImageModel.order == order,
            ),
        ),
        Returning(ProductImageModel),
        session=session,
    )

    await aws_s3.delete_file_from_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
        url=image.image_url,
    )

    return {
        "ok": True,
        "result": True,
    }