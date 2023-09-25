from typing import List

from corecrud import Limit, Offset, Where
from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.app import crud
from core.depends import Authorization, DatabaseSession
from orm import UserSearchModel
from schemas import ApplicationResponse, UserSearch
from schemas.uploads import PaginationUpload
from typing_ import RouteReturnT

router = APIRouter()


async def get_latest_searches_core(
    session: AsyncSession, user_id: int, offset: int, limit: int
) -> List[UserSearch]:
    return await crud.users_searches.select.many(
        Where(UserSearchModel.user_id == user_id),
        Offset(offset),
        Limit(limit),
        session=session,
    )


@router.get(
    path="/latest",
    summary="WORKS (example 5): Get latest searches by user_id.",
    response_model=ApplicationResponse[List[UserSearch]],
    status_code=status.HTTP_200_OK,
)
async def get_latest_searches(
    user: Authorization,
    session: DatabaseSession,
    pagination: PaginationUpload = Depends(),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_latest_searches_core(
            session=session,
            user_id=user.id,
            offset=pagination.offset,
            limit=pagination.limit,
        ),
    }
