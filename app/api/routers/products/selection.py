from typing import Any, List

from corecrud import Correlate, Join, Limit, Offset, Options, OrderBy, SelectFrom, Where
from fastapi import APIRouter
from fastapi.param_functions import Body, Depends, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.app import crud
from core.depends import DatabaseSession
from orm import (
    BundleVariationPodModel,
    BundleVariationPodPriceModel,
    ProductModel,
    SupplierModel,
    VariationValueToProductModel,
)
from schemas import ApplicationResponse, Product, ProductList
from schemas.uploads import (
    PaginationUpload,
    ProductCompilationFiltersUpload,
    ProductSortingUpload,
)
from typing_ import RouteReturnT

router = APIRouter()


async def get_products_list_for_category_core(
    session: AsyncSession,
    pagination: PaginationUpload,
    filters: ProductCompilationFiltersUpload,
    sorting: ProductSortingUpload,
) -> ProductList:
    products = (
        (
            await session.execute(
                select(ProductModel)
                .where(
                    ProductModel.is_active.is_(True),
                    ProductModel.category_id.in_(filters.category_ids)
                    if filters.category_ids
                    else True,
                    (BundleVariationPodPriceModel.discount > 0)
                    if filters.on_sale
                    else (BundleVariationPodPriceModel.discount == 0)
                    if filters.on_sale is False
                    else True,
                )
                .join(
                    BundleVariationPodModel,
                    ProductModel.id == BundleVariationPodModel.product_id,
                )
                .join(
                    BundleVariationPodPriceModel,
                    and_(
                        BundleVariationPodModel.id
                        == BundleVariationPodPriceModel.bundle_variation_pod_id,
                        BundleVariationPodPriceModel.min_quantity
                        == crud.raws.select.executor.query.build(
                            SelectFrom(BundleVariationPodModel),
                            Where(BundleVariationPodModel.product_id == ProductModel.id),
                            Join(
                                BundleVariationPodPriceModel,
                                BundleVariationPodPriceModel.bundle_variation_pod_id
                                == BundleVariationPodModel.id,
                            ),
                            Correlate(ProductModel),
                            nested_select=[func.min(BundleVariationPodPriceModel.min_quantity)],
                        ).as_scalar(),
                    ),
                )
                .options(
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
                    selectinload(ProductModel.supplier).selectinload(SupplierModel.user),
                    selectinload(ProductModel.supplier).selectinload(SupplierModel.company),
                )
                .offset(pagination.offset)
                .limit(pagination.limit)
                .order_by(sorting.sort.by.asc() if sorting.ascending else sorting.sort.by.desc())
            )
        )
        .scalars()
        .all()
    )

    product_models: List[ProductModel] = products

    products_data = await crud.raws.select.one(
        Where(
            ProductModel.is_active.is_(True),
            ProductModel.category_id.in_(filters.category_ids) if filters.category_ids else True,
        ),
        nested_select=[
            func.count(ProductModel.id).label("total_count"),
        ],
        session=session,
    )

    return {
        "total_count": products_data.total_count,
        "products": product_models,
    }


@router.post(
    path="/",
    summary="WORKS: Get list of products",
    description="Available filters: total_orders, date, price, rating",
    response_model=ApplicationResponse[ProductList],
)
async def get_products_list_for_category(
    session: DatabaseSession,
    pagination: PaginationUpload = Depends(),
    filters: ProductCompilationFiltersUpload = Body(...),
    sorting: ProductSortingUpload = Depends(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_products_list_for_category_core(
            session=session,
            pagination=pagination,
            filters=filters,
            sorting=sorting,
        ),
    }


async def get_popular_products_core(
    session: AsyncSession,
    category_id: int,
    offset: int,
    limit: int,
    order_by: Any,
) -> List[ProductModel]:
    return await crud.products.select.many(
        Where(
            and_(
                ProductModel.category_id == category_id,
                ProductModel.is_active.is_(True),
            ),
        ),
        Options(
            selectinload(ProductModel.category),
            selectinload(ProductModel.bundle_variation_pods).selectinload(
                BundleVariationPodModel.prices
            ),
            selectinload(ProductModel.images),
            selectinload(ProductModel.supplier).selectinload(SupplierModel.user),
            selectinload(ProductModel.supplier).selectinload(SupplierModel.company),
        ),
        Offset(offset),
        Limit(limit),
        OrderBy(order_by.desc()),
        session=session,
    )


@router.get(
    path="/popular",
    summary="WORKS (example 1-100): Get popular products in this category.",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_200_OK,
)
async def popular_products(
    session: DatabaseSession,
    category_id: int = Query(...),
    pagination: PaginationUpload = Depends(),
) -> ApplicationResponse[List[Product]]:
    return {
        "ok": True,
        "result": await get_popular_products_core(
            session=session,
            category_id=category_id,
            offset=pagination.offset,
            limit=pagination.limit,
            order_by=ProductModel.total_orders,
        ),
    }


@router.get(
    path="/similar",
    summary="WORKS (example 1-100): Get similar products by product_id.",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_200_OK,
)
async def similar_products(
    session: DatabaseSession,
    category_id: int = Query(...),
    pagination: PaginationUpload = Depends(),
) -> ApplicationResponse[List[Product]]:
    return {
        "ok": True,
        "result": await get_popular_products_core(
            session=session,
            category_id=category_id,
            offset=pagination.offset,
            limit=pagination.limit,
            order_by=ProductModel.grade_average,
        ),
    }
