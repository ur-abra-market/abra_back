from typing import List

from fastapi import APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.depends import DatabaseSession
from orm import BrandModel
from schemas import ApplicationResponse, Brand
from typing_ import RouteReturnT

router = APIRouter()


async def get_all_brands_core(session: AsyncSession) -> List[BrandModel]:
    return (await session.execute(select(BrandModel))).scalars().all()


@router.get(
    path="/",
    summary="WORKS: Get all brands.",
    response_model=ApplicationResponse[List[Brand]],
    status_code=status.HTTP_200_OK,
)
async def get_all_brands(session: DatabaseSession) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_all_brands_core(session=session),
    }
