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
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import join, outerjoin, selectinload
from starlette import status

from core.app import crud
from core.depends import DatabaseSession, SellerAuthorization
from enums import OrderStatus as OrderStatusEnum, PropertyTypeEnum, VariationTypeEnum
from orm import (
    BundleModel,
    BundlePodPriceModel,
    BundleVariationModel,
    BundleVariationPodAmountModel,
    BundleVariationPodModel,
    CategoryModel,
    CompanyModel,
    OrderModel,
    ProductImageModel,
    ProductModel,
    ProductReviewModel,
    PropertyTypeModel,
    PropertyValueModel,
    SellerFavoriteModel,
    SupplierModel,
    UserModel,
    VariationTypeModel,
    VariationValueModel,
    VariationValueToProductModel,
)
from schemas import ApplicationResponse, Order, Product, ProductImage, ProductList
from schemas.uploads import (
    PaginationUpload,
    ProductCompilationFiltersUpload,
    ProductPaginationUpload,
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
    path="/compilation",
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

    print("VALUE", OrderStatusEnum.TO_BE_REVIEWED.value)
    # delete order from cart
    order = await crud.orders.update.one(
        Values(
            {
                OrderModel.is_cart: False,
                OrderModel.order_status_id: OrderStatusEnum.TO_BE_REVIEWED.value,
            }
        ),
        Where(OrderModel.id == order_id),
        Returning(OrderModel.id),
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
    status_id: OrderStatusEnum,
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
    path="/changeOrderStatus/{order_product_variation_id}/{status_id}",
    summary="WORKS: changes the status for the ordered product",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def change_order_status(
    user: SellerAuthorization,
    session: DatabaseSession,
    order_product_variation_id: int = Path(...),
    status_id: OrderStatusEnum = Path(...),
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
    path="/popular",
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
    path="/similar",
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
                    request.sizes and VariationValueModel.value.in_(request.sizes),
                    VariationTypeModel.name == VariationTypeEnum.SIZE,
                ),
            ),
            as_where(
                request.colors,
                and_(
                    request.colors and VariationValueModel.value.in_(request.colors),
                    VariationTypeModel.name == VariationTypeEnum.COLOR,
                ),
            ),
            as_where(
                request.materials,
                and_(
                    request.materials and PropertyValueModel.value.in_(request.materials),
                    PropertyTypeModel.name == PropertyTypeEnum.MATERIAL,
                ),
            ),
            as_where(
                request.age_groups,
                and_(
                    request.age_groups and PropertyValueModel.value.in_(request.age_groups),
                    PropertyTypeModel.name == PropertyTypeEnum.AGE_GROUP,
                ),
            ),
            as_where(
                request.genders,
                and_(
                    request.genders and PropertyValueModel.value.in_(request.genders),
                    PropertyTypeModel.name == PropertyTypeEnum.GENDER,
                ),
            ),
            as_where(
                request.technics,
                and_(
                    request.technics and PropertyValueModel.value.in_(request.technics),
                    PropertyTypeModel.name == PropertyTypeEnum.TECHNICS,
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
            selectinload(ProductModel.properties).joinedload(PropertyValueModel.type),
            selectinload(ProductModel.variations).joinedload(VariationValueModel.type),
        ),
        Offset(offset),
        Limit(limit),
        OrderBy(request.sort_type.by.asc() if request.ascending else request.sort_type.by.desc()),
        session=session,
    )


@router.post(
    path="/pagination",
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
            selectinload(ProductModel.supplier).joinedload(SupplierModel.company),
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
