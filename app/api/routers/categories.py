from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.depends import get_session
from core.tools import store
from schemas import ApplicationResponse, Category, PaginationQuery

router = APIRouter()


@router.get(
    path="/all",
    summary="WORKS: Get all categories.",
    response_model=ApplicationResponse[Category],
    status_code=status.HTTP_200_OK,
)
async def get_all_categories(
    pagination: PaginationQuery = Depends(),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[Category]:
    return {
        "ok": True,
        "result": await store.orm.categories.get_many(
            session=session,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
    }
