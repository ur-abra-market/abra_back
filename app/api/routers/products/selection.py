from typing import Any, List

from corecrud import Limit, Offset, Options, OrderBy, Where
from fastapi import APIRouter
from fastapi.param_functions import Body, Depends, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload, with_expression
from starlette import status

from core.app import crud
from core.depends import AuthorizationOptional, DatabaseSession
from enums import ProductFilterValuesEnum

# from logger import logger
from orm import (
    BrandModel,
    BundleModel,
    BundlePriceModel,
    BundleVariationPodModel,
    CategoryModel,
    ProductModel,
    ProductPriceModel,
    ProductReviewModel,
    ProductVariationPriceModel,
    PropertyValueModel,
    PropertyValueToProductModel,
    SellerFavoriteModel,
    SellerModel,
    SupplierModel,
    UserModel,
    VariationValueToProductModel,
)
from schemas import ApplicationResponse, Product, ProductList
from schemas.uploads import (
    PaginationUpload,
    ProductListFiltersUpload,
    ProductSortingUpload,
)
from typing_ import RouteReturnT

router = APIRouter()


async def get_products_list_core(
    session: AsyncSession,
    pagination: PaginationUpload,
    filters: ProductListFiltersUpload,
    sorting: ProductSortingUpload,
    user: UserModel,
) -> ProductList:
    query = (
        select(
            ProductModel,
        )
        .where(
            ProductModel.is_active.is_(True),
        )
        .outerjoin(ProductModel.prices)
        .group_by(ProductModel.id, sorting.sort.by)
        .order_by(sorting.sort.by.asc() if sorting.ascending else sorting.sort.by.desc())
    )

    query = query.outerjoin(ProductModel.reviews).options(
        with_expression(
            ProductModel.reviews_count, func.coalesce(func.count(ProductReviewModel.id), 0)
        )
    )

    if user and user.seller:
        subquery = select(SellerFavoriteModel.product_id).where(
            SellerFavoriteModel.seller_id == user.seller.id
        )

        query = (
            query.outerjoin(ProductModel.favorites_by_users)
            .group_by(SellerModel.id)
            .options(with_expression(ProductModel.is_favorite, ProductModel.id.in_(subquery)))
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
            query.outerjoin(ProductModel.bundles)
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

    # product brand
    if filters.brand:
        query = query.join(ProductModel.brand).where(BrandModel.id.in_(filters.brand))

    # product property
    if filters.properties:
        query = (
            query.join(PropertyValueToProductModel)
            .join(PropertyValueModel)
            .where(PropertyValueModel.id.in_(filters.properties))
        )

    products: List[ProductModel] = (
        (
            await session.execute(
                query.options(
                    selectinload(ProductModel.category),
                    selectinload(ProductModel.prices),
                    selectinload(ProductModel.brand),
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
                    selectinload(ProductModel.favorites_by_users),
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
    path="/",
    summary="WORKS: Get list of products",
    description="Available filters: total_orders, date, price, rating",
    response_model=ApplicationResponse[ProductList],
    status_code=status.HTTP_200_OK,
)
async def get_products_list(
    user: AuthorizationOptional,
    session: DatabaseSession,
    pagination: PaginationUpload = Depends(),
    sorting: ProductSortingUpload = Depends(),
    filters: ProductListFiltersUpload = Body(...),
) -> RouteReturnT:
    product_list = await get_products_list_core(
        session=session,
        pagination=pagination,
        filters=filters,
        sorting=sorting,
        user=user,
    )
    return {
        "ok": True,
        "result": product_list,
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
            selectinload(ProductModel.prices),
            selectinload(ProductModel.product_variations).selectinload(
                VariationValueToProductModel.prices
            ),
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
