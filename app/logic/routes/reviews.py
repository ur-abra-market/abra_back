from pydantic import BaseModel
from typing import Union, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, update, func, join
from sqlalchemy.ext.asyncio import AsyncSession
from app.logic import utils
from app.logic.consts import *
from app.logic.queries import *
from app.database import get_session
from app.database.models import *
from fastapi_jwt_auth import AuthJWT
import json


class ProductReviewIn(BaseModel):
    product_review_photo: Union[List[str], None]
    product_review_text: str
    product_review_grade: int


class ReactionIn(BaseModel):
    reaction: bool


reviews = APIRouter()


@reviews.post(
    "/{product_id}/make_product_review/",
    summary="WORKS: Create new product review, update grade_average for product. "
    'product_review_photo format is ["URL1", "URL2", ...] or empty [].',
)
async def make_product_review(
    product_review: ProductReviewIn,
    product_id: int,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    seller_id = await Seller.get_seller_id_by_email(user_email)

    is_allowed = await session.execute(
        QUERY_IS_ALOWED_TO_REVIEW.format(seller_id=seller_id, product_id=product_id)
    )
    is_allowed = bool(is_allowed.scalar())
    if is_allowed:
        current_time = utils.get_moscow_datetime()
        grade_average = await session.execute(
            select(Product.grade_average).where(Product.id.__eq__(product_id))
        )
        grade_average = grade_average.scalar()
        if not grade_average:
            grade_average_new = product_review.product_review_grade
        else:
            review_count = await session.execute(
                select(func.count()).where(ProductReview.product_id.__eq__(product_id))
            )
            review_count = review_count.scalar()
            grade_average_new = round(
                (grade_average * review_count + product_review.product_review_grade)
                / (review_count + 1),
                1,
            )
        await session.execute(
            update(Product)
            .where(Product.id.__eq__(product_id))
            .values(grade_average=grade_average_new)
        )
        await session.commit()
        review_data = ProductReview(
            product_id=product_id,
            seller_id=seller_id,
            text=product_review.product_review_text,
            grade_overall=product_review.product_review_grade,
            datetime=current_time,
        )
        session.add(review_data)
        await session.commit()
        product_review_id = await session.execute(
            select(ProductReview.id).where(ProductReview.product_id.__eq__(product_id))
        )
        product_review_id = product_review_id.scalar()
        if product_review.product_review_photo:
            for serial_number, image_url in enumerate(
                product_review.product_review_photo
            ):
                photo_review_data = ProductReviewPhoto(
                    product_review_id=product_review_id,
                    image_url=image_url,
                    serial_number=serial_number,
                )
                session.add(photo_review_data)
            await session.commit()
        # need to make endpoint which checks added review
        await session.commit()
        return JSONResponse(
            status_code=status.HTTP_200_OK, content={"result": "REVIEW_HAS_BEEN_SENT"}
        )
    else:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"result": "METHOD_NOT_ALLOWED"},
        )


@reviews.get(
    "/{product_id}/show_product_review/",
    summary="WORKS: get product_id, skip(def 0), limit(def 10), returns reviews and reactions",
)
async def get_all_product_reviews(
    product_id: int,
    # skip: int = 0,
    # limit: int = 10,
    session: AsyncSession = Depends(get_session),
):
    if not isinstance(product_id, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="INVALID_PRODUCT_ID",
        )

    # query for all product reviews
    product_reviews = await session.execute(
        select(
            ProductReview.seller_id,
            ProductReview.id.label("product_review_id"),
            ProductReview.text,
            ProductReview.grade_overall,
            ProductReview.datetime,
            ProductReviewPhoto.image_url
        ).join(ProductReviewPhoto, right_outer_join=True)\
            .where(ProductReview.id.__eq__(product_id))\
                .order_by(ProductReview.datetime.desc())
    )
    
    # query for all reactions
    reactions = await session.execute(
        select(
            ProductReviewReaction.product_review_id,
            ProductReviewReaction.reaction
        ).join(ProductReview)\
            .where(ProductReview.id.__eq__(product_id))\
                .order_by(ProductReview.datetime.desc())
    )
    # if limit:
    #     quantity = f"LIMIT {limit} OFFSET {skip}"
    #     # product_reviews - query for product reviews with limit
    #     # reactions - query for reactions of each product review
    #     # after else - query without limit
    #     product_reviews = await session.execute(
    #         QUERY_FOR_REVIEWS.format(product_id=product_id, quantity=quantity)
    #     )
    #     reactions = await session.execute(
    #         QUERY_FOR_REACTIONS.format(product_id=product_id, quantity=quantity)
    #     )
    # else:
    #     quantity = ""
    #     product_reviews = await session.execute(
    #         QUERY_FOR_REVIEWS.format(product_id=product_id, quantity=quantity)
    #     )
    #     reactions = await session.execute(
    #         QUERY_FOR_REACTIONS.format(product_id=product_id, quantity=quantity)
    #     )

    product_reviews = [dict(text) for text in product_reviews if product_reviews]
    reactions = [dict(text) for text in reactions if reactions]

    # start of a part of data processing
    urls = []

    for review in product_reviews:
        urls.append((review.get("seller_id"), review.pop("image_url")))
        review["image_url"] = []
    
    for element in urls:
        for review in product_reviews:
            if element[0] == review["seller_id"]:
                review["image_url"].append(element[1])

    product_reviews_result = []

    for review in product_reviews:
        if review not in product_reviews_result:
            product_reviews_result.append(review)
    #end of a part of data processing

    # start of a part of reactions calculating
    reactions_list = []

    for reaction in reactions:
        reactions_list.append((reaction.get("product_review_id"), reaction.pop("reaction")))
        reaction["positive"], reaction["negative"] = [], []

    for element in reactions_list:
        for reaction in reactions:
            if element[0] == reaction["product_review_id"] and element[1]:
                reaction["positive"].append(element[1])
            elif element[0] == reaction["product_review_id"] and not element[1]:
                reaction["negative"].append(element[1])

    reactions_result = []

    for reaction in reactions:
        if reaction not in reactions_result:
            reactions_result.append(reaction)

    for reaction in reactions_result:
            reaction["positive"] = len(reaction["positive"])
            reaction["negative"] = len(reaction["negative"])
    # end of a part od reactions data calculating

    for review in product_reviews_result:
        for reaction in reactions_result:
            if review["product_review_id"] == reaction["product_review_id"]:
                review.update(reaction)

    if product_reviews:
        return JSONResponse(status_code=status.HTTP_200_OK, content=product_reviews_result)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="REVIEWS_NOT_FOUND"
        )


@reviews.post(
    "/{product_review_id}/product_review_reactions/",
    summary="WORKS: query params(product_review_id and seller_id), body (reaction), insert reaction data",
)
async def make_reaction(
    product_review_id: int,
    reaction: ReactionIn,
    Authorize: AuthJWT = Depends(),
    session: AsyncSession = Depends(get_session),
):
    Authorize.jwt_required()
    user_email = json.loads(Authorize.get_jwt_subject())["email"]
    seller_id = await Seller.get_seller_id_by_email(user_email)
    is_product_review_exist = await session.execute(
        select(ProductReview.id).where(ProductReview.id.__eq__(product_review_id))
    )
    is_product_review_exist = is_product_review_exist.scalar()
    if not is_product_review_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="REVIEW_NOT_FOUND"
        )

    reaction_data = ProductReviewReaction(
        seller_id=seller_id,
        product_review_id=product_review_id,
        reaction=reaction.reaction,
    )
    session.add(reaction_data)
    await session.commit()
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"status": "REACTION_HAS_BEEN_SENT"}
    )

