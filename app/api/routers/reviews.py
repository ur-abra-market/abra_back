from typing import List, Optional, Union

from corecrud import (
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
from fastapi.param_functions import Body, Depends, Path
from pydantic import HttpUrl
from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.app import crud
from core.depends import DatabaseSession, SellerAuthorization
from orm import (
    OrderModel,
    OrderProductVariationModel,
    ProductModel,
    ProductReviewModel,
    ProductReviewPhotoModel,
    ProductVariationCountModel,
    VariationValueToProductModel,
)
from schemas import ApplicationResponse, ProductReview
from schemas.uploads import PaginationUpload, ProductReviewUpload
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

    review_count = await crud.raws.select.one(
        Where(ProductReviewModel.product_id == product_id),
        SelectFrom(ProductReviewModel),
        nested_select=[func.count(ProductReviewModel.id)],
        session=session,
    )
    grade_average = round(
        (grade_average * review_count + product_review_grade) / (review_count + 1),
        1,
    )

    return grade_average  # type: ignore[return-value]


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
        Values(
            {
                ProductModel.grade_average: grade_average,
            }
        ),
        Where(ProductModel.id == product_id),
        Returning(ProductModel.id),
        session=session,
    )


async def create_product_review(
    session: AsyncSession,
    product_id: int,
    seller_id: int,
    text: str,
    grade_overall: int,
) -> ProductReviewModel:
    return await crud.products_reviews.insert.one(
        Values(
            {
                ProductReviewModel.product_id: product_id,
                ProductReviewModel.seller_id: seller_id,
                ProductReviewModel.text: text,
                ProductReviewModel.grade_overall: grade_overall,
            }
        ),
        Returning(ProductReviewModel.id),
        session=session,
    )


async def create_product_review_photos(
    session: AsyncSession,
    product_review_id: int,
    product_review_photos: List[HttpUrl],
) -> None:
    await crud.products_reviews_photos.insert.many(
        Values(
            [
                {
                    ProductReviewPhotoModel.product_review_id: product_review_id,
                    ProductReviewPhotoModel.image_url: image_url,
                    ProductReviewPhotoModel.serial_number: serial_number,
                }
                for serial_number, image_url in enumerate(product_review_photos)
            ],
        ),
        Returning(ProductReviewPhotoModel.id),
        session=session,
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
    product = await crud.products.select.one(
        Where(ProductModel.id == product_id),
        session=session,
    )
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
    path="/{product_id}/makeProductReview",
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
    is_allowed = await crud.orders_products_variation.select.one(
        Join(
            OrderModel,
            and_(
                OrderModel.id == OrderProductVariationModel.order_id,
                OrderModel.seller_id == user.seller.id,
                OrderProductVariationModel.status_id == 0,
            ),
        ),
        Join(
            ProductVariationCountModel,
            ProductVariationCountModel.id == OrderProductVariationModel.product_variation_count_id,
        ),
        Join(
            VariationValueToProductModel,
            and_(
                or_(
                    VariationValueToProductModel.id
                    == ProductVariationCountModel.product_variation_value1_id,
                    VariationValueToProductModel.id
                    == ProductVariationCountModel.product_variation_value2_id,
                ),
                VariationValueToProductModel.product_id == product_id,
            ),
        ),
        session=session,
    )
    if not is_allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    await make_product_core(
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
    session: AsyncSession, product_id: int, offset: int, limit: int
) -> List[ProductReviewModel]:
    return await crud.products_reviews.select.many(
        Where(ProductReviewModel.product_id == product_id),
        Options(
            selectinload(ProductReviewModel.photos), selectinload(ProductReviewModel.reactions)
        ),
        Offset(offset),
        Limit(limit),
        OrderBy(ProductReviewModel.datetime.desc()),
        session=session,
    )


@router.post(
    path="/{product_id}/showProductReview",
    summary="WORKS: get product_id, skip(def 0), limit(def 100), returns reviews.",
    response_model=ApplicationResponse[ProductReview],
    status_code=status.HTTP_200_OK,
)
async def show_product_review(
    session: DatabaseSession,
    product_id: int = Path(...),
    pagination: PaginationUpload = Depends(),
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
