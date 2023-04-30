from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.app import crud
from core.depends import get_session
from orm import CountryModel, NumberEmployeesModel
from schemas import ApplicationResponse, Country, NumberEmployees
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
async def get_all_country_codes(session: AsyncSession = Depends(get_session)) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_all_country_core(session=session),
    }


async def get_number_employees_core(session: AsyncSession) -> List[NumberEmployeesModel]:
    return await crud.number_employees.get.many(session=session)


@router.get(
    path="/numberEmployees/",
    summary="WORKS: get options of company number of employees",
    response_model=ApplicationResponse[List[NumberEmployees]],
    status_code=status.HTTP_200_OK,
)
async def get_number_employees(session: AsyncSession = Depends(get_session)) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_number_employees_core(session=session),
    }
