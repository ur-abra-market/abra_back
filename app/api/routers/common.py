from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.app import crud
from core.depends import get_session
from orm import CountryModel
from schemas import ApplicationResponse, Country
from typing_ import RouteReturnT

router = APIRouter()


async def get_all_country_core(session: AsyncSession) -> List[CountryModel]:
    return await crud.country.get.many(session=session)


@router.get(
    path="/country/",
    summary="WORKS: get country and country code",
    response_model=ApplicationResponse[List[Country]],
    status_code=status.HTTP_200_OK,
)
async def get_all_country_codes(
    session: AsyncSession = Depends(get_session),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_all_country_core(session=session),
    }
