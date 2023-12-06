import asyncio
from typing import List

from corecrud import Returning, Values, Where
from fastapi import APIRouter
from fastapi.param_functions import Body, Depends, Path
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload
from starlette import status

from core import exceptions
from core.app import aws_s3, crud
from core.depends import DatabaseSession, Image, SupplierAuthorization, supplier
from core.settings import aws_s3_settings, upload_file_settings
from enums import ProductFilterValuesEnum
from orm import (
    BundlableVariationValueModel,
    BundleModel,
    BundlePriceModel,
    BundleVariationPodModel,
    CategoryModel,
    ProductImageModel,
    ProductModel,
    ProductPriceModel,
    ProductVariationPriceModel,
    PropertyValueToProductModel,
    SupplierModel,
    VariationValueModel,
    VariationValueToProductModel,
)
from schemas import (
    ApplicationResponse,
    Product,
    ProductImage,
    ProductList,
    VariationValueToProduct,
)
from schemas.uploads import (
    BundleUpload,
    PaginationUpload,
    ProductEditUpload,
    ProductSortingUpload,
    ProductUpload,
    SupplierFilterProductListUpload,
)
from typing_ import DictStrAny, RouteReturnT
from utils.misc import result_as_dict
from utils.thumbnail import upload_thumbnail

router = APIRouter(dependencies=[Depends(supplier)])


async def get_product_variations_core(
    supplier_id: int,
    product_id: int,
    session: AsyncSession,
) -> List[VariationValueToProductModel]:
    product = (
        await session.execute(
            select(
                ProductModel,
            )
            .where(
                ProductModel.id == product_id,
                ProductModel.supplier_id == supplier_id,
            )
            .options(
                selectinload(ProductModel.product_variations)
                .selectinload(VariationValueToProductModel.variation)
                .selectinload(VariationValueModel.type)
            )
        )
    ).scalar_one_or_none()

    if not product:
        raise exceptions.NotFoundException(detail="Product not found")

    return product.product_variations


@router.get(
    path="/{product_id}/variations",
    summary="WORKS: Get product variations",
    response_model=ApplicationResponse[List[VariationValueToProduct]],
    status_code=status.HTTP_200_OK,
)
async def get_product_variations(
    user: SupplierAuthorization,
    session: DatabaseSession,
    product_id: int = Path(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_product_variations_core(
            supplier_id=user.supplier.id, product_id=product_id, session=session
        ),
    }


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
                ProductModel.brand_id: 1,
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

    return product


@router.post(
    path="/add",
    summary="WORKS: Add product",
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


async def add_product_bundles_core(
    supplier_id: int,
    product_id: int,
    request: BundleUpload,
    session: AsyncSession,
) -> List[BundlableVariationValueModel]:
    product = (
        await session.execute(
            select(ProductModel.id).where(
                ProductModel.id == product_id,
                ProductModel.supplier_id == supplier_id,
            )
        )
    ).scalar_one_or_none()

    if not product:
        raise exceptions.NotFoundException(detail="Product not found")

    for bundle in request:
        bundle = await crud.bundles.insert.one(
            Values(
                {
                    BundleModel.product_id: product_id,
                }
            ),
            Returning(BundleModel),
            session=session,
        )
        await crud.bundlable_variations_values.insert.many(
            Values(
                [
                    {
                        BundlableVariationValueModel.bundle_id: bundle.id,
                        BundlableVariationValueModel.variation_value_to_product_id: bundle_variation_value_data.variation_value_to_product_id,
                        BundlableVariationValueModel.amount: bundle_variation_value_data.amount,
                    }
                    for bundle_variation_value_data in request.bundlable_variation_values
                ]
            ),
            Returning(BundlableVariationValueModel),
            session=session,
        )


@router.post(
    path="/{product_id}/bundles/add",
    summary="WORKS: Add bundles with variation's amount for product",
    response_model=ApplicationResponse[Product],
    status_code=status.HTTP_200_OK,
)
async def add_product_bundles(
    user: SupplierAuthorization,
    session: DatabaseSession,
    product_id: int = Path(),
    request: List[BundleUpload] = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await add_product_bundles_core(
            request=request, supplier_id=user.supplier.id, product_id=product_id, session=session
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
            # Values(
            #     [
            #         {
            #             ProductPriceModel.product_id: product.id,
            #         }
            #         | price.dict()
            #         for price in request.prices
            #     ],
            # ),
            # Returning(ProductPriceModel.id),
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
    pagination: PaginationUpload,
    filters: SupplierFilterProductListUpload,
    sorting: ProductSortingUpload,
) -> ProductList:
    query = (
        select(ProductModel)
        .where(ProductModel.supplier_id == supplier_id)
        .group_by(ProductModel.id, sorting.sort.by)
        .order_by(sorting.sort.by.asc() if sorting.ascending else sorting.sort.by.desc())
    )

    # active products
    if not filters.is_active == ProductFilterValuesEnum.ALL:
        query = query.where(
            ProductModel.is_active.is_(True)
            if filters.is_active == ProductFilterValuesEnum.TRUE
            else ProductModel.is_active.is_(False)
        )

    # categories
    if filters.category_ids:
        CategoryModelParent = aliased(CategoryModel)
        CategoryModelGrandParent = aliased(CategoryModel)
        query = (
            query.join(ProductModel.category)
            .join(CategoryModelParent, CategoryModel.parent)
            .join(CategoryModelGrandParent, CategoryModelParent.parent)
            .where(
                or_(
                    CategoryModel.id.in_(filters.category_ids),
                    CategoryModelParent.id.in_(filters.category_ids),
                    CategoryModelGrandParent.id.in_(filters.category_ids),
                )
            )
        )

    if filters.price_range:
        query = query.where(
            and_(
                ProductPriceModel.value <= filters.price_range.max_price,
                ProductPriceModel.value >= filters.price_range.min_price,
            )
        )

    # on_sale
    if not filters.on_sale == ProductFilterValuesEnum.ALL:
        query = (
            query.outerjoin(ProductModel.prices)
            .outerjoin(ProductModel.bundles)
            .outerjoin(BundleModel.prices)
            .outerjoin(ProductModel.product_variations)
            .outerjoin(VariationValueToProductModel.prices)
            .where(
                (
                    or_(
                        ProductPriceModel.discount != 0,
                        BundlePriceModel.discount != 0,
                        ProductVariationPriceModel.discount != 0,
                    )
                )
                if filters.on_sale == ProductFilterValuesEnum.TRUE
                else (
                    and_(
                        ProductPriceModel.discount == 0,
                        BundlePriceModel.discount == 0,
                        ProductVariationPriceModel.discount == 0,
                    )
                )
            )
        )

    # product name
    if filters.query:
        names = [ProductModel.name.icontains(name) for name in filters.query.split()]
        query = query.where(or_(*names))

    products: List[ProductModel] = (
        (
            await session.execute(
                query.options(
                    selectinload(ProductModel.category),
                    selectinload(ProductModel.prices),
                    selectinload(ProductModel.product_variations).selectinload(
                        VariationValueToProductModel.prices
                    ),
                    selectinload(ProductModel.bundles),
                    selectinload(ProductModel.bundle_variation_pods).selectinload(
                        BundleVariationPodModel.prices
                    ),
                    selectinload(ProductModel.images),
                    # selectinload(ProductModel.supplier).selectinload(SupplierModel.user),
                    selectinload(ProductModel.supplier).selectinload(SupplierModel.company),
                )
                .offset(pagination.offset)
                .limit(pagination.limit)
            )
        )
        .scalars()
        .unique()
        .all()
    )

    products_total_count = (
        await session.execute(select(func.count()).select_from(query))
    ).scalar_one()

    return {
        "total_count": products_total_count,
        "products": products,
    }


@router.post(
    path="",
    summary="WORKS: Get list of all suppliers products.",
    response_model=ApplicationResponse[ProductList],
    status_code=status.HTTP_200_OK,
)
async def products(
    user: SupplierAuthorization,
    session: DatabaseSession,
    pagination: PaginationUpload = Depends(),
    sorting: ProductSortingUpload = Depends(),
    filters: SupplierFilterProductListUpload = Body(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await manage_products_core(
            session=session,
            supplier_id=user.supplier.id,
            pagination=pagination,
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
    path="/{product_id}/images/{order}/upload",
    summary="WORKS: Uploads provided product image to AWS S3 and saves url to DB",
    response_model=ApplicationResponse[ProductImage],
    status_code=status.HTTP_200_OK,
)
async def upload_product_image(
    file: Image,
    user: SupplierAuthorization,
    session: DatabaseSession,
    product_id: int = Path(...),
    order: int = Path(...),
) -> RouteReturnT:
    link = await aws_s3.upload_file_to_s3(
        bucket_name=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET, file=file
    )
    thumbnail_urls_list: list[DictStrAny] = await asyncio.gather(
        *[
            result_as_dict(
                func=upload_thumbnail,
                key_name=f"thumbnail_{size[0]}",
                file=file,
                bucket=aws_s3_settings.AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET,
                size=size,
            )
            for size in upload_file_settings.PRODUCT_THUMBNAIL_PROPERTIES
        ]
    )

    thumbnail_urls = {key: value for item in thumbnail_urls_list for key, value in item.items()}

    product = await crud.products.select.one(
        Where(
            and_(ProductModel.id == product_id, ProductModel.supplier_id == user.supplier.id),
        ),
        session=session,
    )
    if not product:
        raise exceptions.NotFoundException(
            detail="Product not found",
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
        raise exceptions.AlreadyExistException(
            detail="Try another order",
        )

    product_image = await crud.products_images.insert.one(
        Values(
            {
                ProductImageModel.image_url: link,
                ProductImageModel.product_id: product_id,
                ProductImageModel.order: order,
                ProductImageModel.thumbnail_urls: thumbnail_urls,
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
    path="/{product_id}/images/{order}/delete",
    summary="WORKS: Delete provided product image from AWS S3 and url from DB",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def delete_product_image(
    session: DatabaseSession,
    product_id: int = Path(...),
    order: int = Path(...),
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
