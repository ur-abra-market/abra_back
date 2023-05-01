from typing import Any, List, cast

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends, Path, Query
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import join, joinedload, outerjoin
from starlette import status

from core.app import crud
from core.depends import UserObjects, auth_required, get_session
from enums import OrderStatus
from orm import (
    OrderModel,
    OrderProductVariationModel,
    ProductImageModel,
    ProductModel,
    ProductPriceModel,
    ProductReviewModel,
    ProductVariationCountModel,
    ProductVariationValueModel,
    SellerFavoriteModel,
    SupplierModel,
)
from schemas import (
    ApplicationResponse,
    Product,
    ProductImage,
    QueryPaginationRequest,
    QueryProductCompilationRequest,
)
from typing_ import RouteReturnT

router = APIRouter()


async def get_products_list_for_category_core(
    session: AsyncSession,
    pagination: QueryPaginationRequest,
    filters: QueryProductCompilationRequest,
) -> List[ProductModel]:
    order_by = filters.get_order_by()

    return await crud.products.get.many_unique(
        session=session,
        where=[
            ProductModel.is_active.is_(True),
            ProductModel.category_id == filters.category_id if filters.category_id else None,
        ],
        join=[
            [
                ProductPriceModel,
                and_(
                    ProductModel.id == ProductPriceModel.product_id,
                    ProductPriceModel.min_quantity
                    == crud.raws.get.query(
                        func.min(ProductPriceModel.min_quantity),
                        where=[
                            and_(
                                ProductPriceModel.product_id == ProductModel.id,
                                func.now().between(
                                    ProductPriceModel.start_date, ProductPriceModel.end_date
                                ),
                            )
                        ],
                        select_from=[ProductPriceModel],
                        correlate=True,
                        correlate_by=[ProductModel],
                    ).as_scalar(),
                ),
            ]
        ],
        options=[
            joinedload(ProductModel.prices),
            joinedload(ProductModel.images),
            joinedload(ProductModel.supplier).joinedload(SupplierModel.user),
        ],
        offset=pagination.offset,
        limit=pagination.limit,
        order_by=[order_by],
    )


@router.get(
    path="/compilation/",
    summary="WORKS: Get list of products",
    description="Available filters: total_orders, date, price, rating",
    response_model=ApplicationResponse[List[Product]],
)
async def get_products_list_for_category(
    pagination: QueryPaginationRequest = Depends(QueryPaginationRequest),
    filters: QueryProductCompilationRequest = Depends(QueryProductCompilationRequest),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_products_list_for_category_core(
            session=session,
            pagination=pagination,
            filters=filters,
        ),
    }


@router.get(
    path="/{product_id}/grades/",
    summary="WORKS: get all reviews grades information",
    response_model=ApplicationResponse[RouteReturnT],
    status_code=status.HTTP_200_OK,
)
async def get_review_grades_info(
    product_id: int = Path(...),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    grade_info = await crud.raws.get.one(
        ProductModel.grade_average,
        func.count(ProductReviewModel.id).label("reviews_count"),
        session=session,
        where=[ProductModel.id == product_id],
        group_by=[ProductModel.grade_average],
        select_from=[
            outerjoin(
                ProductModel,
                ProductReviewModel,
                ProductReviewModel.product_id == ProductModel.id,
            ),
        ],
    )

    review_details = await crud.raws.get.many(
        ProductReviewModel.grade_overall,
        func.count(ProductReviewModel.id).label("review_count"),
        session=session,
        where=[ProductReviewModel.product_id == product_id],
        group_by=[ProductReviewModel.grade_overall],
        order_by=[ProductReviewModel.grade_overall.desc()],
        select_from=[ProductReviewModel],
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
    seller_favorite = await crud.sellers_favorites.get.one(
        session=session,
        where=[
            and_(
                SellerFavoriteModel.seller_id == seller_id,
                SellerFavoriteModel.product_id == product_id,
            )
        ],
    )
    if seller_favorite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already in favorites",
        )

    await crud.sellers_favorites.insert.one(
        session=session,
        values={
            SellerFavoriteModel.seller_id: seller_id,
            SellerFavoriteModel.product_id: product_id,
        },
    )


@router.post(
    path="/addFavorite/",
    summary="WORKS: add product in favorite",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def add_favorite(
    product_id: int = Query(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    if not user.orm.seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")

    await add_favorite_core(
        seller_id=user.schema.seller.id, product_id=product_id, session=session
    )

    return {
        "ok": True,
        "result": True,
    }


async def remove_favorite_core(product_id: int, seller_id: int, session: AsyncSession) -> None:
    await crud.sellers_favorites.delete.one(
        session=session,
        where=and_(
            SellerFavoriteModel.seller_id == seller_id,
            SellerFavoriteModel.product_id == product_id,
        ),
    )


@router.delete(
    path="/removeFavorite/",
    summary="WORKS: remove product in favorite",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def remove_favorite(
    product_id: int = Query(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    if not user.orm.seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")

    await remove_favorite_core(
        seller_id=user.schema.seller.id, product_id=product_id, session=session
    )

    return {
        "ok": True,
        "result": True,
    }


async def get_product_images_core(
    product_id: int,
    session: AsyncSession,
) -> List[ProductImageModel]:
    return await crud.products_images.get.many(
        session=session, where=[ProductImageModel.product_id == product_id]
    )


@router.get(
    path="/{product_id}/images/",
    summary="WORKS: Get product images by product_id.",
    response_model=ApplicationResponse[List[ProductImage]],
    status_code=status.HTTP_200_OK,
)
async def get_product_images(
    product_id: int = Path(...),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_product_images_core(product_id=product_id, session=session),
    }


async def show_cart_core(
    session: AsyncSession,
    seller_id: int,
) -> List[Any]:
    return await crud.raws.get.many(  # type: ignore[no-any-return]
        OrderModel.id.label("order_id"),
        OrderModel.seller_id,
        ProductModel.name.label("product_name"),
        ProductModel.description.label("product_description"),
        OrderProductVariationModel.count.label("cart_count"),
        ProductVariationCountModel.count.label("stock_count"),
        ProductPriceModel.value.label("price_value"),
        ProductPriceModel.discount,
        session=session,
        where=[
            OrderModel.seller_id == seller_id,
            OrderModel.is_cart.is_(True),
            ProductVariationCountModel.id == OrderProductVariationModel.product_variation_count_id,
            ProductVariationValueModel.product_id == ProductModel.id,
        ],
        select_from=[
            join(
                OrderModel,
                OrderProductVariationModel,
                OrderModel.id == OrderProductVariationModel.order_id,
            ),
            join(
                ProductVariationValueModel,
                ProductVariationCountModel,
                ProductVariationCountModel.product_variation_value1_id
                == ProductVariationValueModel.id,
            ),
            join(ProductModel, ProductPriceModel, ProductModel.id == ProductPriceModel.product_id),
        ],
    )


@router.get(
    path="/showCart/",
    summary="WORKS: Show seller cart.",
    response_model=ApplicationResponse[List[RouteReturnT]],
    status_code=status.HTTP_200_OK,
)
async def show_cart(
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    if not user.orm.seller:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seller not found",
        )

    return {
        "ok": True,
        "result": await show_cart_core(
            session=session,
            seller_id=user.schema.seller.id,
        ),
    }


async def create_order_core(
    order_id: int,
    seller_id: int,
    session: AsyncSession,
) -> None:
    order = await crud.orders.get.one(
        session=session,
        where=[and_(OrderModel.id == order_id, OrderModel.seller_id == seller_id)],
    )

    if not order or not order.is_cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Specified invalid order id",
        )

    # delete order from cart
    order = await crud.orders.update.one(
        session=session,
        values={OrderModel.is_cart: False},
        where=OrderModel.id == order_id,
    )

    order_product_variation = await crud.orders_products_variation.get.one(
        session=session, where=[OrderProductVariationModel.order_id == order.id]
    )

    # subtract ordered amount from amount in stock
    await crud.products_variation_counts.update.one(
        session=session,
        values={
            ProductVariationCountModel.count: ProductVariationCountModel.count
            - order_product_variation.count
        },
        where=ProductVariationCountModel.id == order_product_variation.product_variation_count_id,
    )

    # change order status
    await crud.orders_products_variation.update.one(
        session=session,
        values={OrderProductVariationModel.status_id: OrderStatus.paid.value},
        where=OrderProductVariationModel.order_id == order.id,
    )


@router.post(
    path="/createOrder/{order_id}",
    description="Turn cart into order (after successful payment)",
    summary="WORKS: create order from a cart.",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def create_order(
    order_id: int = Path(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    if not user.orm.seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")

    await create_order_core(order_id=order_id, seller_id=user.schema.seller.id, session=session)

    return {
        "ok": True,
        "result": True,
    }


async def change_order_status_core(
    session: AsyncSession,
    order_product_variation_id: int,
    seller_id: int,
    status_id: OrderStatus,
) -> None:
    order_product_variation = await crud.orders_products_variation.get.one(
        session=session,
        where=[OrderProductVariationModel.id == order_product_variation_id],
    )
    if not order_product_variation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order product variation not found"
        )

    # check the order exists and is connected to the current seller
    order = await crud.orders.get.one(
        session=session,
        where=[
            and_(
                OrderModel.id == order_product_variation.order_id,
                OrderModel.seller_id == seller_id,
            )
        ],
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    await crud.orders_products_variation.update.one(
        session=session,
        values={
            OrderProductVariationModel.status_id: status_id.value,
        },
        where=OrderProductVariationModel.id == order_product_variation_id,
    )


@router.put(
    path="/changeOrderStatus/{order_product_variation_id}/{status_id}/",
    summary="WORKS: changes the status for the ordered product",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def change_order_status(
    order_product_variation_id: int = Path(...),
    status_id: OrderStatus = Path(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    if not user.orm.seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")

    await change_order_status_core(
        session=session,
        order_product_variation_id=order_product_variation_id,
        seller_id=user.schema.seller.id,
        status_id=status_id,
    )

    return {
        "ok": True,
        "result": True,
    }


async def get_popular_products_core(
    session: AsyncSession,
    product_id: int,
    category_id: int,
    offset: int,
    limit: int,
    order_by: Any,
) -> List[Any]:
    return await crud.products.get.many_unique(
        session=session,
        where=[
            and_(
                ProductModel.id != product_id,
                ProductModel.category_id == category_id,
                ProductModel.is_active.is_(True),
            )
        ],
        join=[
            [
                ProductPriceModel,
                and_(
                    ProductModel.id == ProductPriceModel.product_id,
                    ProductPriceModel.min_quantity
                    == crud.raws.get.query(
                        func.min(ProductPriceModel.min_quantity),
                        where=[
                            and_(
                                ProductPriceModel.product_id == product_id,
                                func.now().between(
                                    ProductPriceModel.start_date, ProductPriceModel.end_date
                                ),
                            )
                        ],
                        select_from=[ProductPriceModel],
                        correlate=True,
                        correlate_by=[ProductModel],
                    ).as_scalar(),
                ),
            ]
        ],
        options=[joinedload(ProductModel.prices)],
        offset=offset,
        limit=limit,
        order_by=[order_by],
    )


async def get_category_id(session: AsyncSession, product_id: int) -> int:
    category_id = await crud.raws.get.one(
        ProductModel.category_id,
        session=session,
        where=[ProductModel.id == product_id],
        select_from=[ProductModel],
    )

    return cast(int, category_id)


@router.get(
    path="/popular/",
    summary="WORKS (example 1-100): Get popular products in this category.",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_200_OK,
)
async def popular_products(
    product_id: int = Query(...),
    pagination: QueryPaginationRequest = Depends(),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[Product]]:
    category_id = await get_category_id(session=session, product_id=product_id)

    return {
        "ok": True,
        "result": await get_popular_products_core(
            session=session,
            product_id=product_id,
            category_id=category_id,
            offset=pagination.offset,
            limit=pagination.limit,
            order_by=ProductModel.total_orders,
        ),
    }


@router.get(
    path="/similar/",
    summary="WORKS (example 1-100): Get similar products by product_id.",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_200_OK,
)
async def similar_products(
    product_id: int = Query(...),
    pagination: QueryPaginationRequest = Depends(),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[Product]]:
    category_id = await get_category_id(session=session, product_id=product_id)

    return {
        "ok": True,
        "result": await get_popular_products_core(
            session=session,
            product_id=product_id,
            category_id=category_id,
            offset=pagination.offset,
            limit=pagination.limit,
            order_by=ProductModel.grade_average,
        ),
    }
