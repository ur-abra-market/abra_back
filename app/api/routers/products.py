from typing import Any, List

from corecrud import (
    Correlate,
    GroupBy,
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
from sqlalchemy import and_, func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import outerjoin, selectinload
from starlette import status

from core.app import crud
from core.depends import DatabaseSession, SellerAuthorization
from enums import OrderStatus as OrderStatusEnum
from orm import (
    BundleModel,
    BundlePodPriceModel,
    BundleVariationModel,
    BundleVariationPodAmountModel,
    BundleVariationPodModel,
    OrderModel,
    OrderStatusHistoryModel,
    OrderStatusModel,
    ProductImageModel,
    ProductModel,
    ProductReviewModel,
    SellerFavoriteModel,
    SupplierModel,
)
from schemas import ApplicationResponse, Order, Product, ProductImage, ProductList
from schemas.uploads import (
    PaginationUpload,
    ProductCompilationFiltersUpload,
    ProductSortingUpload,
    StatusDataUpload,
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
                    (BundlePodPriceModel.discount > 0)
                    if filters.on_sale
                    else (BundlePodPriceModel.discount == 0)
                    if filters.on_sale is False
                    else True,
                )
                .join(
                    BundleVariationPodModel,
                    ProductModel.id == BundleVariationPodModel.product_id,
                )
                .join(
                    BundlePodPriceModel,
                    and_(
                        BundleVariationPodModel.id == BundlePodPriceModel.bundle_variation_pod_id,
                        BundlePodPriceModel.min_quantity
                        == crud.raws.select.executor.query.build(
                            SelectFrom(BundleVariationPodModel),
                            Where(BundleVariationPodModel.product_id == ProductModel.id),
                            Join(
                                BundlePodPriceModel,
                                BundlePodPriceModel.bundle_variation_pod_id
                                == BundleVariationPodModel.id,
                            ),
                            Correlate(ProductModel),
                            nested_select=[func.min(BundlePodPriceModel.min_quantity)],
                        ).as_scalar(),
                    ),
                )
                .options(
                    selectinload(ProductModel.category),
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
    path="",
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


@router.get(
    path="/{product_id}/grades",
    summary="WORKS: get all reviews grades information",
    response_model=ApplicationResponse[RouteReturnT],
    status_code=status.HTTP_200_OK,
)
async def get_review_grades_info(
    session: DatabaseSession,
    product_id: int = Path(...),
) -> RouteReturnT:
    grade_info = await crud.raws.select.one(
        Where(ProductModel.id == product_id),
        GroupBy(ProductModel.grade_average),
        SelectFrom(
            outerjoin(
                ProductModel,
                ProductReviewModel,
                ProductReviewModel.product_id == ProductModel.id,
            ),
        ),
        nested_select=[
            ProductModel.grade_average,
            func.count(ProductReviewModel.id).label("reviews_count"),
        ],
        session=session,
    )

    review_details = await crud.raws.select.many(
        Where(ProductReviewModel.product_id == product_id),
        GroupBy(ProductReviewModel.grade_overall),
        OrderBy(ProductReviewModel.grade_overall.desc()),
        SelectFrom(ProductReviewModel),
        nested_select=[
            ProductReviewModel.grade_overall,
            func.count(ProductReviewModel.id).label("review_count"),
        ],
        session=session,
    )

    return {
        "ok": True,
        "result": {
            "grade_average": grade_info.grade_average,
            "review_count": grade_info.reviews_count,
            "details": review_details,
        },
    }


async def add_favorite_core(product_id: int, seller_id: int, session: AsyncSession) -> None:
    seller_favorite = await crud.sellers_favorites.select.one(
        Where(
            and_(
                SellerFavoriteModel.seller_id == seller_id,
                SellerFavoriteModel.product_id == product_id,
            ),
        ),
        session=session,
    )
    if seller_favorite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already in favorites",
        )

    await crud.sellers_favorites.insert.one(
        Values(
            {
                SellerFavoriteModel.seller_id: seller_id,
                SellerFavoriteModel.product_id: product_id,
            }
        ),
        Returning(SellerFavoriteModel.id),
        session=session,
    )


@router.post(
    path="/addFavorite",
    summary="WORKS: add product in favorite",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def add_favorite(
    user: SellerAuthorization,
    session: DatabaseSession,
    product_id: int = Query(...),
) -> RouteReturnT:
    await add_favorite_core(seller_id=user.seller.id, product_id=product_id, session=session)

    return {
        "ok": True,
        "result": True,
    }


async def remove_favorite_core(product_id: int, seller_id: int, session: AsyncSession) -> None:
    await crud.sellers_favorites.delete.one(
        Where(
            and_(
                SellerFavoriteModel.seller_id == seller_id,
                SellerFavoriteModel.product_id == product_id,
            ),
        ),
        Returning(SellerFavoriteModel.id),
        session=session,
    )


@router.delete(
    path="/removeFavorite",
    summary="WORKS: remove product in favorite",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def remove_favorite(
    user: SellerAuthorization,
    session: DatabaseSession,
    product_id: int = Query(...),
) -> RouteReturnT:
    await remove_favorite_core(seller_id=user.seller.id, product_id=product_id, session=session)

    return {
        "ok": True,
        "result": True,
    }


async def get_product_images_core(
    product_id: int,
    session: AsyncSession,
) -> List[ProductImageModel]:
    return await crud.products_images.select.many(
        Where(ProductImageModel.product_id == product_id),
        session=session,
    )


@router.get(
    path="/{product_id}/images",
    summary="WORKS: Get product images by product_id.",
    response_model=ApplicationResponse[List[ProductImage]],
    status_code=status.HTTP_200_OK,
)
async def get_product_images(
    session: DatabaseSession,
    product_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_product_images_core(product_id=product_id, session=session),
    }


async def show_cart_core(
    session: AsyncSession,
    seller_id: int,
) -> List[OrderModel]:
    return await crud.orders.select.many(
        Where(
            OrderModel.seller_id == seller_id,
            OrderModel.is_cart.is_(True),
        ),
        Options(
            selectinload(OrderModel.details)
            .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
            .selectinload(BundleVariationPodModel.product),
            selectinload(OrderModel.details)
            .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
            .selectinload(BundleVariationPodModel.prices),
            selectinload(OrderModel.details)
            .selectinload(BundleVariationPodAmountModel.bundle_variation_pod)
            .selectinload(BundleVariationPodModel.bundle_variations)
            .selectinload(BundleVariationModel.bundle)
            .selectinload(BundleModel.variation_values),
        ),
        session=session,
    )


@router.get(
    path="/showCart",
    summary="WORKS: Show seller cart.",
    response_model=ApplicationResponse[List[Order]],
    status_code=status.HTTP_200_OK,
)
async def show_cart(
    user: SellerAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await show_cart_core(
            session=session,
            seller_id=user.seller.id,
        ),
    }


async def create_order_core(
    order_id: int,
    seller_id: int,
    session: AsyncSession,
) -> None:
    order = await crud.orders.select.one(
        Where(and_(OrderModel.id == order_id, OrderModel.seller_id == seller_id)),
        session=session,
    )

    if not order or not order.is_cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified invalid order id",
        )
    # delete order from cart
    order = await crud.orders.update.one(
        Values(
            {
                OrderModel.is_cart: False,
            }
        ),
        Where(OrderModel.id == order_id),
        Returning(OrderModel),
        session=session,
    )

    await session.execute(
        insert(OrderStatusHistoryModel).values(
            {
                OrderStatusHistoryModel.order_id: order.id,
                OrderStatusHistoryModel.order_status_id: (
                    select(OrderStatusModel.id)
                    .where(OrderStatusModel.name == OrderStatusEnum.PENDING.value)
                    .scalar_subquery()
                ),
            }
        )
    )


@router.post(
    path="/createOrder/{order_id}",
    description="Turn cart into order (after successful payment)",
    summary="WORKS: create order from a cart.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def create_order(
    user: SellerAuthorization,
    session: DatabaseSession,
    order_id: int = Path(...),
) -> RouteReturnT:
    await create_order_core(order_id=order_id, seller_id=user.seller.id, session=session)

    return {
        "ok": True,
        "result": True,
    }


async def change_order_status_core(
    session: AsyncSession,
    order_id: int,
    seller_id: int,
    status: StatusDataUpload,
) -> None:
    order = await crud.orders.select.one(
        Where(
            OrderModel.id == order_id,
            OrderModel.seller_id == seller_id,
        ),
        session=session,
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    await session.execute(
        insert(OrderStatusHistoryModel).values(
            {
                OrderStatusHistoryModel.order_id: order_id,
                OrderStatusHistoryModel.order_status_id: (
                    select(OrderStatusModel.id)
                    .where(OrderStatusModel.name == status)
                    .scalar_subquery()
                ),
            }
        )
    )


@router.put(
    path="/changeOrderStatus/{order_id}",
    summary="WORKS: changes the status for the ordered product",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def change_order_status(
    user: SellerAuthorization,
    session: DatabaseSession,
    order_id: int = Path(...),
    status: OrderStatusEnum = Query(),
) -> RouteReturnT:
    await change_order_status_core(
        session=session,
        order_id=order_id,
        seller_id=user.seller.id,
        status=status.value,
    )

    return {
        "ok": True,
        "result": True,
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


async def get_info_for_product_card_core(
    session: AsyncSession,
    product_id: int,
) -> ProductModel:
    return await crud.products.select.one(
        Where(ProductModel.id == product_id),
        Options(
            selectinload(ProductModel.category),
            selectinload(ProductModel.bundle_variation_pods).selectinload(
                BundleVariationPodModel.prices
            ),
            selectinload(ProductModel.images),
            selectinload(ProductModel.supplier).selectinload(SupplierModel.user),
            selectinload(ProductModel.supplier).selectinload(SupplierModel.company),
            selectinload(ProductModel.tags),
        ),
        session=session,
    )


@router.get(
    path="/productCard/{product_id}",
    summary="WORKS (example 1-100, 1): Get info for product card p1.",
    response_model=ApplicationResponse[Product],
    status_code=status.HTTP_200_OK,
)
async def get_info_for_product_card(
    session: DatabaseSession,
    product_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_info_for_product_card_core(session=session, product_id=product_id),
    }
