from typing import Dict, List, Optional

from corecrud import GroupBy, OrderBy, SelectFrom, Where
from fastapi import APIRouter
from fastapi.param_functions import Body, Depends, Path
from pydantic import HttpUrl
from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import outerjoin, selectinload, with_expression
from starlette import status

from core import exceptions
from core.app import crud
from core.depends import DatabaseSession, SellerAuthorization
from enums import OrderStatus as OrderStatusEnum
from orm import (
    BundleVariationPodAmountModel,
    BundleVariationPodModel,
    OrderModel,
    OrderStatusHistoryModel,
    OrderStatusModel,
    SupplierModel,
)
from orm.product import ProductModel, ProductReviewModel, ProductReviewPhotoModel
from schemas import ApplicationResponse, Reviews
from schemas.uploads import PaginationUpload, ProductGradesUpload, ProductReviewUpload
from typing_ import RouteReturnT

router = APIRouter()


async def make_product_review_core(
    session: AsyncSession,
    product_id: int,
    review_grade: int,
    seller_id: int,
    text: str,
    photos: Optional[List[HttpUrl]] = None,
) -> None:
    product = (
        await session.execute(
            select(ProductModel).where(ProductModel.id == product_id),
        )
    ).scalar_one()

    # Count the number of reviews for the product
    review_count = (
        await session.execute(
            select(func.count(ProductReviewModel.id)).where(
                ProductReviewModel.product_id == product_id
            )
        )
    ).scalar_one()

    # Calculate the new grade_average
    grade_average = (
        round((float(product.grade_average) * review_count + review_grade) / (review_count + 1), 1)
        if review_count
        else review_grade
    )
    product.grade_average = grade_average

    # Add new review
    new_review_id = (
        await session.execute(
            insert(ProductReviewModel)
            .values(
                product_id=product_id,
                seller_id=seller_id,
                text=text,
                grade_overall=review_grade,
            )
            .returning(ProductReviewModel.id)
        )
    ).scalar_one()

    if photos:
        photo_data = [
            ProductReviewPhotoModel(
                product_review_id=new_review_id,
                image_url=image_url,
                serial_number=serial_number,
            )
            for serial_number, image_url in enumerate(photos)
        ]
        await session.execute(insert(ProductReviewPhotoModel).values(photo_data))


@router.post(
    path="/add",
    summary="WORKS: Create new product review, update grade_average for product. product_review_photo format is ['URL1', 'URL2', ...] or empty [].",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def make_product_review(
    user: SellerAuthorization,
    session: DatabaseSession,
    request: ProductReviewUpload = Body(...),
    product_id: int = Path(...),
) -> RouteReturnT:
    # Check if the seller has any completed orders for the product
    is_allowed = (
        await session.execute(
            select(OrderModel)
            .join(OrderStatusHistoryModel)
            .join(OrderStatusModel)
            .join(BundleVariationPodAmountModel)
            .join(BundleVariationPodModel)
            .where(
                OrderModel.seller_id == user.seller.id,
                OrderStatusModel.name == OrderStatusEnum.COMPLETED.value,
                OrderModel.is_cart is False,
                BundleVariationPodModel.product_id == product_id,
            )
        )
    ).scalar_one_or_none()

    if not is_allowed:
        raise exceptions.ForbiddenException(detail="Not allowed")

    await make_product_review_core(
        session=session,
        product_id=product_id,
        review_grade=request.product_review_grade,
        seller_id=user.seller.id,
        text=request.product_review_text,
        photos=request.product_review_photo,
    )

    return {
        "ok": True,
        "result": True,
    }


async def show_product_review_core(
    session: AsyncSession,
    product_id: int,
    pagination: PaginationUpload,
    grade: int = None,
    with_photos: bool = None,
) -> Dict:
    query_product = (
        select(ProductModel)
        .where(ProductModel.id == product_id)
        .group_by(ProductModel.id)
        .options(selectinload(ProductModel.supplier).selectinload(SupplierModel.company))
        .options(selectinload(ProductModel.images))
        .outerjoin(ProductModel.reviews)
        .options(
            with_expression(
                ProductModel.reviews_count, func.coalesce(func.count(ProductReviewModel.id), 0)
            )
        )
    )

    product = (await session.execute(query_product)).scalar()

    query_review = (
        select(ProductReviewModel)
        .where(ProductReviewModel.product_id == product_id)
        .options(selectinload(ProductReviewModel.photos))
        .offset(pagination.offset)
        .limit(pagination.limit)
    )

    if with_photos:
        query_review = query_review.filter(ProductReviewModel.photos.any())

    if grade is not None:
        query_review = query_review.where(ProductReviewModel.grade_overall == grade)

    product_review = (await session.execute(query_review)).scalars().all()

    rating_list = (
        await session.execute(
            select(ProductReviewModel.grade_overall, func.count())
            .where(ProductReviewModel.product_id == product_id)
            .group_by(ProductReviewModel.grade_overall)
        )
    ).fetchall()

    feedbacks = {key: value for key, value in rating_list}

    for i in range(1, 6):
        if i not in feedbacks:
            feedbacks[i] = 0

    return {
        "product": product,
        "product_review": product_review,
        "feedbacks": feedbacks,
    }


@router.post(
    path="",
    summary="WORKS: get product_id, skip(def 0), limit(def 100), returns reviews.",
    response_model=ApplicationResponse[Reviews],
    status_code=status.HTTP_200_OK,
)
async def show_product_review(
    session: DatabaseSession,
    product_id: int = Path(...),
    request: ProductGradesUpload = Depends(),
    pagination: PaginationUpload = Depends(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await show_product_review_core(
            session=session,
            product_id=product_id,
            pagination=pagination,
            grade=request.grade,
            with_photos=request.with_photos,
        ),
    }


@router.get(
    path="/grades",
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
