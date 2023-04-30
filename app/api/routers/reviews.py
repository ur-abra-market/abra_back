from typing import List, Optional, Union, cast

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Body, Depends, Path
from pydantic import HttpUrl
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.app import crud
from core.depends import UserObjects, auth_required, get_session
from orm import ProductModel, ProductReviewModel, ProductReviewPhotoModel
from schemas import (
    ApplicationResponse,
    BodyProductReviewRequest,
    ProductReview,
    QueryPaginationRequest,
)
from typing_ import RouteReturnT

router = APIRouter()


async def calculate_grade_average(
    session: AsyncSession,
    product_id: int,
    product_review_grade: int,
    grade_average: Optional[float] = None,
) -> Union[int, float]:
    if not grade_average:
        return product_review_grade

    review_count = cast(
        int,
        await crud.raws.get.one(
            func.count(ProductReviewModel.id),
            session=session,
            where=[ProductReviewModel.product_id == product_id],
            select_from=[ProductReviewModel],
        ),
    )
    grade_average = round(
        (grade_average * review_count + product_review_grade) / (review_count + 1),
        1,
    )

    return grade_average


async def update_product_grave_average(
    session: AsyncSession,
    product_id: int,
    product_review_grade: int,
    grade_average: Optional[float] = None,
) -> None:
    grade_average = await calculate_grade_average(
        session=session,
        product_id=product_id,
        product_review_grade=product_review_grade,
        grade_average=grade_average,
    )
    await crud.products.update.one(
        session=session,
        values={
            ProductModel.grade_average: grade_average,
        },
        where=ProductModel.id == product_id,
    )


async def create_product_review(
    session: AsyncSession,
    product_id: int,
    seller_id: int,
    text: str,
    grade_overall: int,
) -> ProductReviewModel:
    return await crud.products_reviews.insert.one(
        session=session,
        values={
            ProductReviewModel.product_id: product_id,
            ProductReviewModel.seller_id: seller_id,
            ProductReviewModel.text: text,
            ProductReviewModel.grade_overall: grade_overall,
        },
    )


async def create_product_review_photos(
    session: AsyncSession,
    product_review_id: int,
    product_review_photos: List[HttpUrl],
) -> None:
    await crud.products_reviews_photos.insert.many(
        session=session,
        values=[
            {
                ProductReviewPhotoModel.product_review_id: product_review_id,
                ProductReviewPhotoModel.image_url: image_url,
                ProductReviewPhotoModel.serial_number: serial_number,
            }
            for serial_number, image_url in enumerate(product_review_photos)
        ],
    )


async def fully_create_product_review(
    session: AsyncSession,
    product_id: int,
    seller_id: int,
    text: str,
    grade_overall: int,
    photos: Optional[List[HttpUrl]] = None,
) -> None:
    product_review = await create_product_review(
        session=session,
        product_id=product_id,
        seller_id=seller_id,
        text=text,
        grade_overall=grade_overall,
    )
    if photos:
        await create_product_review_photos(
            session=session,
            product_review_id=product_review.id,
            product_review_photos=photos,
        )


async def make_product_core(
    session: AsyncSession,
    product_id: int,
    review_grade: int,
    seller_id: int,
    text: str,
    photos: Optional[List[HttpUrl]] = None,
) -> None:
    product = await crud.products.by.one(session=session, id=product_id)
    await update_product_grave_average(
        session=session,
        product_id=product_id,
        product_review_grade=review_grade,
        grade_average=product.grade_average,
    )

    await fully_create_product_review(
        session=session,
        product_id=product.id,
        seller_id=seller_id,
        text=text,
        grade_overall=review_grade,
        photos=photos,
    )


@router.post(
    path="/{product_id}/makeProductReview/",
    summary="WORKS: Create new product review, update grade_average for product. product_review_photo format is ['URL1', 'URL2', ...] or empty [].",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/{product_id}/make_product_review/",
    description="Moved to /reviews/{product_id}/makeProductReview",
    deprecated=True,
    summary="WORKS: Create new product review, update grade_average for product. product_review_photo format is ['URL1', 'URL2', ...] or empty [].",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def make_product_review(
    request: BodyProductReviewRequest = Body(...),
    product_id: int = Path(...),
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    is_allowed = await crud.orders_products_variation.is_allowed(
        session=session, product_id=product_id, seller_id=user.schema.seller.id
    )
    if not is_allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    await make_product_core(
        session=session,
        product_id=product_id,
        review_grade=request.product_review_grade,
        seller_id=user.schema.seller.id,
        text=request.product_review_text,
        photos=request.product_review_photo,
    )

    return {
        "ok": True,
        "result": True,
    }


async def show_product_review_core(
    session: AsyncSession, product_id: int, offset: int, limit: int
) -> List[ProductReviewModel]:
    return await crud.products_reviews.by.many(
        session=session,
        product_id=product_id,
        options=[joinedload(ProductReviewModel.photos), joinedload(ProductReviewModel.reactions)],
        offset=offset,
        limit=limit,
        order_by=[ProductReviewModel.datetime.desc()],
    )


@router.post(
    path="/{product_id}/showProductReview/",
    summary="WORKS: get product_id, skip(def 0), limit(def 100), returns reviews.",
    response_model=ApplicationResponse[ProductReview],
    status_code=status.HTTP_200_OK,
)
@router.post(
    path="/{product_id}/show_product_review/",
    description="Moved to /reviews/{product_id}/showProductReview",
    deprecated=True,
    summary="WORKS: get product_id, skip(def 0), limit(def 100), returns reviews.",
    response_model=ApplicationResponse[ProductReview],
    status_code=status.HTTP_308_PERMANENT_REDIRECT,
)
async def show_product_review(
    product_id: int = Path(...),
    pagination: QueryPaginationRequest = Depends(),
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await show_product_review_core(
            session=session,
            product_id=product_id,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
    }
