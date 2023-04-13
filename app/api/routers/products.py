# mypy: disable-error-code="arg-type,return-value"

from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, outerjoin
from starlette import status

from core.depends import auth_optional, get_session
from core.orm import orm
from orm import ProductModel, ProductPriceModel, ProductReviewModel, SupplierModel
from schemas import (
    ApplicationResponse,
    ProductListResponse,
    ProductReviewGradesResponse,
    QueryPaginationRequest,
    QueryProductCompilationRequest,
)

router = APIRouter()


@router.get(
    path="/compilation/",
    dependencies=[Depends(auth_optional)],
    summary="WORKS: Get list of products",
    description="Available filters: total_orders, date, price, rating",
    response_model=ApplicationResponse[ProductListResponse],
)
async def get_products_list_for_category(
    query_pagination: QueryPaginationRequest = Depends(QueryPaginationRequest),
    query_filters: QueryProductCompilationRequest = Depends(QueryProductCompilationRequest),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[ProductListResponse]:
    # TODO: Maybe unite this route with POST /pagination ?
    product_sorting_types_map = {
        "rating": ProductModel.grade_average,
        "price": ProductPriceModel.value,
        "date": ProductModel.datetime,
        "total_orders": ProductModel.total_orders,
    }

    order_by = []
    if query_filters.order_by:
        # convert human readable sort type to field in DB
        order_by_field = product_sorting_types_map.get(query_filters.order_by.value, None)

        if order_by_field and query_filters.order_by.value == "date":
            order_by.append(order_by_field.desc())
        elif order_by_field:
            order_by.append(order_by_field)

    product_list = await orm.products.get_many_unique(
        session=session,
        where=[
            ProductModel.is_active.__eq__(True),
            ProductModel.category_id == query_filters.category_id
            if query_filters.category_id
            else None,
        ],
        options=[
            joinedload(ProductModel.prices),
            joinedload(ProductModel.images),
            joinedload(ProductModel.supplier).joinedload(SupplierModel.user),
        ],
        limit=query_pagination.limit,
        offset=query_pagination.offset,
        order_by=[
            *order_by,
        ],
    )

    return {
        "ok": True,
        "result": {
            "total": len(product_list),
            "products": product_list,
        },
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
