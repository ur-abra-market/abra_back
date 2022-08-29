from classes.response_models import *
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, text, and_, or_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from logic import utils
from logic.consts import *
from database import get_session
from database.models import *


reviews = APIRouter()


@reviews.post("/{product_id}/make-product-review/",
              summary="WORKS: query params(product_id, seller_id) count new average grade, sends reviews")
async def make_product_review(product_review: ProductReviewIn,
                              product_id: int,
                              seller_id: int,
                              session: AsyncSession = Depends(get_session)):
    is_allowed = await session\
        .execute(select(Order.id)\
                 .where(Order.product_id.__eq__(product_id) \
                      & Order.seller_id.__eq__(seller_id) \
                      & Order.status_id.__eq__(4)))
    is_allowed = is_allowed.scalar()
    current_time = utils.get_moscow_datetime()
    if is_allowed:
        grade_average = await session\
                              .execute(select(Product.grade_average)\
                                       .where(Product.id.__eq__(product_id)))
        grade_average = grade_average.scalar()
        if not grade_average:
            grade_average_new = product_review.product_review_grade
        else:
            review_count = await session\
                             .execute(select(func.count())\
                                      .where(ProductReview.product_id.__eq__(product_id)))
            review_count = review_count.scalar()
            grade_average_new = round((grade_average * review_count + product_review.product_review_grade)\
                                / (review_count + 1), 1)
        await session.execute(update(Product)\
                              .where(Product.id.__eq__(product_id))\
                              .values(grade_average=grade_average_new))
        await session.commit()
        review_data = ProductReview(
            product_id=product_id,
            seller_id=seller_id,
            text=product_review.product_review_text,
            grade_overall=product_review.product_review_grade,
            datetime=current_time
        )
        session.add(review_data)
        await session.commit()
        product_review_id = await session\
                                  .execute(select(ProductReview.id)\
                                           .where(ProductReview.product_id.__eq__(product_id)))
        product_review_id = product_review_id.scalar()
        if product_review.product_review_photo:
            photo_review_data = ProductReviewPhoto(
                product_review_id=product_review_id,
                image_url=product_review.product_review_photo
            )
            session.add(photo_review_data)
            await session.commit()
        # next execute() need to change because of is_completed
        await session.execute(update(Order)\
                              .where(Order.product_id.__eq__(product_id) & Order.seller_id.__eq__(seller_id))\
                              .values(is_completed=0))
        await session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"result": "REVIEW_HAS_BEEN_SENT"}
        )
    else:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"result": "METHOD_NOT_ALLOWED"}
        )


@reviews.get("/{product_id}/show-product-review/",
              summary="WORKS: get product_id, skip(def 0), limit(def 10), returns reviews")
async def get_10_product_reviews(product_id: int,
                                 skip: int = 0,
                                 limit: int = 10,
                                 session: AsyncSession = Depends(get_session)):
    if not isinstance(product_id, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PRODUCT_ID"
        )
    if limit:
        quantity = f"LIMIT {limit} OFFSET {skip}"
        product_reviews = await session\
                                .execute(QUERY_FOR_REVIEWS.format(product_id=product_id, quantity=quantity))
    else:
        quantity = ""
        product_reviews = await session\
                                .execute(QUERY_FOR_REVIEWS.format(product_id=product_id, quantity=quantity))
    product_reviews = [dict(text) for text in product_reviews if product_reviews]
    if product_reviews:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=product_reviews
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="REVIEWS_NOT_FOUND"
        )


@reviews.post("/{product_review_id}/product-review-reactions/",
              summary="WORKS: query params(product_review_id and seller_id), body (reaction), insert reaction data")
async def make_reaction(product_review_id: int,
                        seller_id: int,
                        reaction: ReactionIn,
                        session: AsyncSession = Depends(get_session)):
    reaction_data = ProductReviewReaction(
        seller_id=seller_id,
        product_review_id=product_review_id,
        reaction=reaction.reaction
    )
    session.add(reaction_data)
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "REACTION_HAS_BEEN_SENT"}
    )