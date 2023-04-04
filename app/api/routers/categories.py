from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from starlette import status

from core.depends import get_session
from core.tools import store
from orm import CategoryModel
from schemas import ApplicationResponse, Category

router = APIRouter()


@router.get(
    path="/all/",
    summary="WORKS: Get all categories.",
    response_model=ApplicationResponse[List[Category]],
    status_code=status.HTTP_200_OK,
)
async def get_all_categories(
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[List[Category]]:
    return {
        "ok": True,
        "result": await store.orm.categories.get_many_unique(
            session=session, options=[joinedload(CategoryModel.childs)]
        ),
    }
