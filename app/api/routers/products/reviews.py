from typing import Dict, List, Optional, Union

from corecrud import GroupBy, OrderBy, Returning, SelectFrom, Values, Where
from fastapi import APIRouter
from fastapi.param_functions import Body, Depends, Path
from pydantic import HttpUrl
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import outerjoin, selectinload, with_expression
from starlette import status

from core import exceptions
from core.app import crud
from core.depends import DatabaseSession, SellerAuthorization
from orm import SupplierModel
from orm.product import ProductModel, ProductReviewModel, ProductReviewPhotoModel
from schemas import ApplicationResponse, Reviews
from schemas.uploads import PaginationUpload, ProductGradesUpload, ProductReviewUpload
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
    is_allowed = await crud.orders_products_variation.select.one(
        # Join(
        #     OrderModel,
        #     and_(
        #         OrderModel.id == OrderProductVariationModel.order_id,
        #         OrderModel.seller_id == user.seller.id,
        #         OrderProductVariationModel.status_id == 0,
        #     ),
        # ),
        # Join(
        #     ProductVariationCountModel,
        #     ProductVariationCountModel.id == OrderProductVariationModel.product_variation_count_id,
        # ),
        # Join(
        #     VariationValueToProductModel,
        #     and_(
        #         or_(
        #             VariationValueToProductModel.id
        #             == ProductVariationCountModel.product_variation_value1_id,
        #             VariationValueToProductModel.id
        #             == ProductVariationCountModel.product_variation_value2_id,
        #         ),
        #         VariationValueToProductModel.product_id == product_id,
        #     ),
        # ),
        session=session,
    )
    if not is_allowed:
        raise exceptions.ForbiddenException(detail="Not allowed")

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
    )

    query_product = query_product.outerjoin(ProductModel.reviews).options(
        with_expression(
            ProductModel.reviews_count, func.coalesce(func.count(ProductReviewModel.id), 0)
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
