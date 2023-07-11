from typing import Any, List, Optional

from corecrud import (
    Correlate,
    Filter,
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
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import join, outerjoin, selectinload
from starlette import status

from core.app import crud
from core.depends import DatabaseSession, SellerAuthorization
from enums import CategoryPropertyTypeEnum, CategoryVariationTypeEnum, OrderStatus
from orm import (
    CategoryPropertyTypeModel,
    CategoryPropertyValueModel,
    CategoryVariationTypeModel,
    CategoryVariationValueModel,
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
    PaginationUpload,
    Product,
    ProductCompilationUpload,
    ProductImage,
    ProductPaginationUpload,
)
from typing_ import RouteReturnT

router = APIRouter()


async def get_products_list_for_category_core(
    session: AsyncSession,
    pagination: PaginationUpload,
    filters: ProductCompilationUpload,
) -> List[ProductModel]:
    return await crud.products.select.many(
        Where(
            ProductModel.is_active.is_(True),
            True if not filters.category_id else ProductModel.category_id == filters.category_id,
        ),
        Options(
            selectinload(ProductModel.prices),
            selectinload(ProductModel.images),
            selectinload(ProductModel.supplier).joinedload(SupplierModel.user),
        ),
        Offset(pagination.offset),
        Limit(pagination.limit),
        OrderBy(filters.sort_type.by.asc() if filters.ascending else filters.sort_type.by.desc()),
        session=session,
    )


@router.post(
    path="/compilation/",
    summary="WORKS: Get list of products",
    description="Available filters: total_orders, date, price, rating",
    response_model=ApplicationResponse[List[Product]],
)
async def get_products_list_for_category(
    session: DatabaseSession,
    pagination: PaginationUpload = Depends(),
    filters: ProductCompilationUpload = Body(...),
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
    path="/addFavorite/",
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
    path="/removeFavorite/",
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
    path="/{product_id}/images/",
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
) -> List[Any]:
    return await crud.raws.select.many(
        Where(
            OrderModel.seller_id == seller_id,
            OrderModel.is_cart.is_(True),
            ProductVariationCountModel.id == OrderProductVariationModel.product_variation_count_id,
            ProductVariationValueModel.product_id == ProductModel.id,
        ),
        SelectFrom(
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
        ),
        nested_select=[
            OrderModel.id.label("order_id"),
            OrderModel.seller_id,
            ProductModel.name.label("product_name"),
            ProductModel.description.label("product_description"),
            OrderProductVariationModel.count.label("cart_count"),
            ProductVariationCountModel.count.label("stock_count"),
            ProductPriceModel.value.label("price_value"),
            ProductPriceModel.discount,
        ],
        session=session,
    )


@router.get(
    path="/showCart/",
    summary="WORKS: Show seller cart.",
    response_model=ApplicationResponse[List[RouteReturnT]],
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
        Values({OrderModel.is_cart: False}),
        Where(OrderModel.id == order_id),
        Returning(OrderModel.id),
        session=session,
    )

    order_product_variation = await crud.orders_products_variation.select.one(
        Where(OrderProductVariationModel.order_id == order.id),
        session=session,
    )

    # subtract ordered amount from amount in stock
    await crud.products_variation_counts.update.one(
        Values(
            {
                ProductVariationCountModel.count: ProductVariationCountModel.count
                - order_product_variation.count
            }
        ),
        Where(ProductVariationCountModel.id == order_product_variation.product_variation_count_id),
        Returning(ProductVariationCountModel.id),
        session=session,
    )

    # change order status
    await crud.orders_products_variation.update.one(
        Values({OrderProductVariationModel.status_id: OrderStatus.PAID.value}),
        Where(OrderProductVariationModel.order_id == order.id),
        Returning(OrderProductVariationModel.id),
        session=session,
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
    order_product_variation_id: int,
    seller_id: int,
    status_id: OrderStatus,
) -> None:
    order_product_variation = await crud.orders_products_variation.select.one(
        Where(OrderProductVariationModel.id == order_product_variation_id),
        session=session,
    )
    if not order_product_variation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order product variation not found"
        )

    # check the order exists and is connected to the current seller
    order = await crud.orders.select.one(
        Where(
            and_(
                OrderModel.id == order_product_variation.order_id,
                OrderModel.seller_id == seller_id,
            ),
        ),
        session=session,
    )
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    await crud.orders_products_variation.update.one(
        Values(
            {
                OrderProductVariationModel.status_id: status_id.value,
            }
        ),
        Where(OrderProductVariationModel.id == order_product_variation_id),
        Returning(OrderProductVariationModel.id),
        session=session,
    )


@router.put(
    path="/changeOrderStatus/{order_product_variation_id}/{status_id}/",
    summary="WORKS: changes the status for the ordered product",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def change_order_status(
    user: SellerAuthorization,
    session: DatabaseSession,
    order_product_variation_id: int = Path(...),
    status_id: OrderStatus = Path(...),
) -> RouteReturnT:
    await change_order_status_core(
        session=session,
        order_product_variation_id=order_product_variation_id,
        seller_id=user.seller.id,
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
) -> List[ProductModel]:
    return await crud.products.select.many(
        Where(
            and_(
                ProductModel.id != product_id,
                ProductModel.category_id == category_id,
                ProductModel.is_active.is_(True),
            ),
        ),
        Join(
            ProductPriceModel,
            and_(
                ProductModel.id == ProductPriceModel.product_id,
                ProductPriceModel.min_quantity
                == crud.raws.select.executor.query.build(
                    Where(
                        and_(
                            ProductPriceModel.product_id == product_id,
                            func.now().between(
                                ProductPriceModel.start_date, ProductPriceModel.end_date
                            ),
                        ),
                    ),
                    SelectFrom(ProductPriceModel),
                    Correlate(ProductModel),
                    nested_select=[func.min(ProductPriceModel.min_quantity)],
                ).as_scalar(),
            ),
        ),
        Options(
            selectinload(ProductModel.prices),
            selectinload(ProductModel.images),
        ),
        Offset(offset),
        Limit(limit),
        OrderBy(order_by),
        session=session,
    )


async def get_category_id(session: AsyncSession, product_id: int) -> int:
    product = await crud.raws.select.one(
        Where(ProductModel.id == product_id),
        SelectFrom(ProductModel),
        nested_select=[ProductModel.category_id],
        session=session,
    )

    return product.category_id


@router.get(
    path="/popular/",
    summary="WORKS (example 1-100): Get popular products in this category.",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_200_OK,
)
async def popular_products(
    session: DatabaseSession,
    product_id: int = Query(...),
    pagination: PaginationUpload = Depends(),
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
    session: DatabaseSession,
    product_id: int = Query(...),
    pagination: PaginationUpload = Depends(),
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


async def get_products_core(
    session: AsyncSession,
    request: ProductPaginationUpload,
    offset: int,
    limit: int,
) -> List[ProductModel]:
    def as_where(value: Optional[Any], condition: Any) -> Any:
        return True if not value else condition

    return await crud.products.select.many_unique(
        Filter(
            ProductModel.is_active.is_(True),
            as_where(request.category_id, ProductModel.category_id == request.category_id),
            as_where(
                request.sizes,
                and_(
                    request.sizes and CategoryVariationValueModel.value.in_(request.sizes),
                    CategoryVariationTypeModel.name == CategoryVariationTypeEnum.SIZE,
                ),
            ),
            as_where(
                request.colors,
                and_(
                    request.colors and CategoryVariationValueModel.value.in_(request.colors),
                    CategoryVariationTypeModel.name == CategoryVariationTypeEnum.COLOR,
                ),
            ),
            as_where(
                request.materials,
                and_(
                    request.materials and CategoryPropertyValueModel.value.in_(request.materials),
                    CategoryPropertyTypeModel.name == CategoryPropertyTypeEnum.MATERIAL,
                ),
            ),
            as_where(
                request.age_groups,
                and_(
                    request.age_groups
                    and CategoryPropertyValueModel.value.in_(request.age_groups),
                    CategoryPropertyTypeModel.name == CategoryPropertyTypeEnum.AGE_GROUP,
                ),
            ),
            as_where(
                request.genders,
                and_(
                    request.genders and CategoryPropertyValueModel.value.in_(request.genders),
                    CategoryPropertyTypeModel.name == CategoryPropertyTypeEnum.GENDER,
                ),
            ),
            as_where(
                request.technics,
                and_(
                    request.technics and CategoryPropertyValueModel.value.in_(request.technics),
                    CategoryPropertyTypeModel.name == CategoryPropertyTypeEnum.TECHNICS,
                ),
            ),
        ),
        Join(
            ProductPriceModel,
            and_(
                ProductModel.id == ProductPriceModel.product_id,
                func.now().between(ProductPriceModel.start_date, ProductPriceModel.end_date),
                as_where(request.min_price, ProductPriceModel.value >= request.min_price),
                as_where(request.max_price, ProductPriceModel.value <= request.max_price),
                as_where(request.with_discount, func.coalesce(ProductPriceModel.discount, 0) > 0),
            ),
        ),
        Options(
            selectinload(ProductModel.prices),
            selectinload(ProductModel.supplier).joinedload(SupplierModel.user),
            selectinload(ProductModel.properties).joinedload(CategoryPropertyValueModel.type),
            selectinload(ProductModel.variations).joinedload(CategoryVariationValueModel.type),
        ),
        Offset(offset),
        Limit(limit),
        OrderBy(request.sort_type.by.asc() if request.ascending else request.sort_type.by.desc()),
        session=session,
    )


@router.post(
    path="/pagination/",
    summary="WORKS: Pagination for products list page (sort_type = rating/price/date).",
    response_model=ApplicationResponse[List[Product]],
    status_code=status.HTTP_200_OK,
)
async def product_pagination(
    session: DatabaseSession,
    pagination: PaginationUpload = Depends(),
    request: ProductPaginationUpload = Body(...),
) -> ApplicationResponse[List[Product]]:
    return {
        "ok": True,
        "result": await get_products_core(
            session=session,
            request=request,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
    }


async def get_info_for_product_card_core(
    session: AsyncSession,
    product_id: int,
) -> ProductModel:
    return await crud.products.select.one(
        Where(ProductModel.id == product_id),
        Options(
            selectinload(ProductModel.prices),
            selectinload(ProductModel.images),
            selectinload(ProductModel.category),
            selectinload(ProductModel.tags),
            selectinload(ProductModel.supplier),
            selectinload(ProductModel.variations),
        ),
        session=session,
    )


@router.get(
    path="/productCard/{product_id}/",
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
