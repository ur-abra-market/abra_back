from fastapi import APIRouter
from fastapi.param_functions import Depends
from starlette import status
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from orm import (
    ProductModel,
    ProductReviewModel,
)
from core.depends import auth_optional, UserObjects, get_session
from core.tools import store
from schemas import (
    ApplicationResponse,
    ProductReviewGradesOut,
)

router = APIRouter()


@router.get(
    path="/{product_id}/grades/",
    dependencies=[Depends(auth_optional)],
    summary="WORKS: get all reviews grades by product_id",
    response_model=ApplicationResponse[ProductReviewGradesOut],
    status_code=status.HTTP_200_OK,
)
async def get_grade_and_count(
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    grade_average_info = await store.orm.products.get_one(
        ProductModel.grade_average,
        func.count(ProductReviewModel.id),
        session=session,
        where=[ProductModel.id == product_id],
        options=[
            joinedload(ProductModel.reviews),
        ],
    )

    review_details = await store.orm.products.get_many(
        ProductReviewModel.grade_overall,
        func.count(ProductReviewModel.id),
        session=session,
        where=[ProductModel.id == product_id],
        options=[
            joinedload(ProductModel.reviews),
        ],
    )

    return {
        "ok": True,
        "result": {
            "info": grade_average_info,
            "details": review_details,
        },
    }
