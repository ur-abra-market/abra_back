# mypy: disable-error-code="arg-type,return-value"
from typing import Any, Dict, List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends, Path
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import join, joinedload, outerjoin
from starlette import status

from core.depends import UserObjects, auth_required, get_session
from core.orm import orm
from orm import (
    OrderModel,
    OrderProductVariationModel,
    ProductImageModel,
    ProductModel,
    ProductPriceModel,
    ProductReviewModel,
    ProductVariationCountModel,
    ProductVariationValueModel,
    SupplierModel,
)
from schemas import (
    ApplicationResponse,
    Product,
    ProductImage,
    QueryPaginationRequest,
    QueryProductCompilationRequest,
)

router = APIRouter()


async def get_products_list_for_category_core(
    session: AsyncSession,
    pagination: QueryPaginationRequest,
    filters: QueryProductCompilationRequest,
) -> List[ProductModel]:
    return await orm.products.get_many_unique(  # type: ignore[no-any-return]
        session=session,
        where=[
            ProductModel.is_active.is_(True),
            ProductModel.category_id == filters.category_id if filters.category_id else None,
        ],
        options=[
            joinedload(ProductModel.prices),
            joinedload(ProductModel.images),
            joinedload(ProductModel.supplier).joinedload(SupplierModel.user),
        ],
        offset=pagination.offset,
        limit=pagination.limit,
        order_by=filters.get_order_by(),
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
) -> ApplicationResponse[List[Product]]:
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
    response_model=ApplicationResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
)
async def get_review_grades_info(
    product_id: int = Path(...),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[Dict[str, Any]]:
    grade_info = await orm.raws.get_one(
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

    review_details = await orm.raws.get_many(
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


async def get_product_images_core(
    product_id: int,
    session: AsyncSession,
) -> List[ProductImageModel]:
    return await orm.products_images.get_one_by(session=session, product_id=product_id)  # type: ignore[no-any-return]


@router.get(
    path="/{product_id}/images/",
    summary="WORKS: Get product images by product_id.",
    response_model=ApplicationResponse[List[ProductImage]],
    status_code=status.HTTP_200_OK,
)
async def get_product_images(
    product_id: int = Path(...),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[ProductImage]]:
    return {
        "ok": True,
        "result": await get_product_images_core(product_id=product_id, session=session),
    }


async def show_cart_core(
    session: AsyncSession,
    seller_id: int,
) -> List[Any]:
    return await orm.raws.get_many(  # type: ignore[no-any-return]
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
    response_model=ApplicationResponse[List[Dict[str, Any]]],
    status_code=status.HTTP_200_OK,
)
@router.get(
    path="/show_cart/",
    description="Moved to /products/showCart",
    deprecated=True,
    summary="WORKS: Show seller cart.",
    response_model=ApplicationResponse[List[Dict[str, Any]]],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def show_cart(
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[Dict[str, Any]]]:
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
