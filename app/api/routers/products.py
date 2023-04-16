# mypy: disable-error-code="arg-type,return-value"

from typing import List

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Depends, Path, Query
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, outerjoin
from starlette import status

from core.depends import UserObjects, auth_required, get_session
from core.orm import orm
from orm import ProductModel, ProductReviewModel, SellerFavoriteModel, SupplierModel
from schemas import (
    ApplicationResponse,
    Product,
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
    response_model=ApplicationResponse[ProductReviewGradesResponse],
    status_code=status.HTTP_200_OK,
)
async def get_review_grades_info(
    product_id: int = Path(...),
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


# noinspection PyUnusedLocal
@router.patch(
    path="/favorite_product/",
    description="Moved to POST /products/addFavorite, DELETE /products/removeFavorite",
    deprecated=True,
    status_code=status.HTTP_418_IM_A_TEAPOT,
)
async def favorite_product_deprecated(
    product_id: int = Query(...),
    is_favorite: bool = Query(...),
) -> None:
    raise HTTPException(
        status_code=status.HTTP_418_IM_A_TEAPOT,
        detail="Frontend, change paths быро",  # noqa
    )


async def add_favorite_core(product_id: int, seller_id: int, session: AsyncSession) -> None:
    seller_favorite = await orm.sellers_favorites.get_one(
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

    await orm.sellers_favorites.insert_one(
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
) -> ApplicationResponse[bool]:
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
    await orm.sellers_favorites.delete_one(
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
) -> ApplicationResponse[bool]:
    if not user.orm.seller:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Seller not found")

    await remove_favorite_core(
        seller_id=user.schema.seller.id, product_id=product_id, session=session
    )

    return {
        "ok": True,
        "result": True,
    }
