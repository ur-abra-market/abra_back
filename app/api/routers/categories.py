from typing import List

from corecrud import Options
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from core.app import crud
from core.depends import DatabaseSession
from orm import CategoryModel
from schemas import ApplicationResponse, Category
from typing_ import RouteReturnT

router = APIRouter()


async def get_all_categories_core(session: AsyncSession) -> List[CategoryModel]:
    return await crud.categories.select.many(
        Options(selectinload(CategoryModel.children)),
        session=session,
    )


@router.get(
    path="/all/",
    summary="WORKS: Get all categories.",
    response_model=ApplicationResponse[List[Category]],
    status_code=status.HTTP_200_OK,
)
async def get_all_categories(session: DatabaseSession) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_all_categories_core(session=session),
    }
