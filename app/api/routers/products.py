# mypy: disable-error-code="arg-type,return-value"

from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, outerjoin
from starlette import status

from core.depends import auth_optional, get_session
from core.orm import orm
from orm import ProductImageModel, ProductModel, ProductReviewModel, SupplierModel
from schemas import (
    ApplicationResponse,
    Product,
    ProductImagesResponse,
    ProductReviewGradesResponse,
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
            ProductModel.is_active.__eq__(True),
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
    dependencies=[Depends(auth_optional)],
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
    dependencies=[Depends(auth_optional)],
    summary="WORKS: get all reviews grades information",
    response_model=ApplicationResponse[ProductReviewGradesResponse],
    status_code=status.HTTP_200_OK,
)
async def get_review_grades_info(
    product_id: int,
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[ProductReviewGradesResponse]:
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


@router.get(
    path="/{product_id}/images/",
    dependencies=[Depends(auth_optional)],
    summary="Get product images by product_id.",
    response_model=ApplicationResponse[ProductImagesResponse],
    status_code=status.HTTP_200_OK,
)
async def get_product_images(
    product_id: int,
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[ProductImagesResponse]:
    images = await orm.raws.get_many(
        ProductImageModel.image_url,
        ProductImageModel.serial_number,
        session=session,
        where=[ProductImageModel.product_id == product_id],
        select_from=[ProductImageModel],
    )

    return {
        "ok": True,
        "result": {"images": images},
    }
