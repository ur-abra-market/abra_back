from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.depends import auth_optional, get_session
from core.tools import tools
from orm import (
    ProductImageModel,
    ProductModel,
    ProductPriceModel,
    ProductReviewModel,
    SupplierModel,
)
from schemas import (
    ApplicationResponse,
    ProductListOut,
    ProductReviewGradesOut,
    QueryPaginationRequest,
    QueryProductCompilationRequest,
)

router = APIRouter()


@router.get(
    path="/compilation/",
    dependencies=[Depends(auth_optional)],
    summary="WORKS: Get list of products",
    description="Available filters: total_orders, date, price, rating",
    response_model=ApplicationResponse[ProductListOut],
)
async def get_products_list_for_category(
    query_pagination: QueryPaginationRequest = Depends(QueryPaginationRequest),
    query_filters: QueryProductCompilationRequest = Depends(QueryProductCompilationRequest),
    session: AsyncSession = Depends(get_session),
):
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

    product_list = await tools.store.orm.products.get_many(
        ProductModel,
        ProductPriceModel,
        ProductImageModel,
        SupplierModel,
        session=session,
        where=[
            ProductModel.is_active == 1,
            ProductModel.category_id == query_filters.category_id
            if query_filters.category_id
            else None,
        ],
        join=[
            [ProductPriceModel, ProductPriceModel.product_id == ProductModel.id],
            [ProductImageModel, ProductImageModel.product_id == ProductModel.id],
        ],
        options=[
            joinedload(ProductModel.supplier),
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
    response_model=ApplicationResponse[ProductReviewGradesOut],
    status_code=status.HTTP_200_OK,
)
async def get_review_grades_info(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    grade_info = await tools.store.orm.products.get_many(
        ProductModel.grade_average,
        func.count(ProductReviewModel.id),
        session=session,
        where=[ProductModel.id == product_id],
        options=[
            joinedload(ProductModel.reviews),
        ],
        group_by=[ProductModel.grade_average],
    )

    # print("GV", grade_info)

    # review_details = await tools.store.orm.products.get_many(
    #     ProductReviewModel.grade_overall,
    #     func.count(ProductReviewModel.id),
    #     session=session,
    #     where=[ProductModel.id == product_id],
    #     options=[
    #         joinedload(ProductModel.reviews),
    #     ],
    #     group_by=[ProductReviewModel.grade_overall],
    #     order_by=[ProductReviewModel.grade_overall.desc()],
    # )

    return {
        "ok": True,
        "result": {
            "grade_average": grade_info.grade_average,
            "review_count": grade_info.count,
            # "details": review_details,
        },
    }
