from typing import List

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.app import crud
from core.depends import DatabaseSession
from orm import CountryModel, EmployeesNumberModel
from schemas import ApplicationResponse, Country, EmployeesNumber
from typing_ import RouteReturnT

router = APIRouter()


async def get_all_country_core(session: AsyncSession) -> List[CountryModel]:
    return await crud.country.select.many(session=session)


@router.get(
    path="/countries",
    summary="WORKS: get country and country code",
    response_model=ApplicationResponse[List[Country]],
    status_code=status.HTTP_200_OK,
)
async def get_all_country_codes(session: DatabaseSession) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_all_country_core(session=session),
    }


async def get_employees_number_core(session: AsyncSession) -> List[EmployeesNumberModel]:
    return await crud.employees_number.select.many(session=session)


@router.get(
    path="/employeesNumbers",
    summary="WORKS: get options of company number of employees",
    response_model=ApplicationResponse[List[EmployeesNumber]],
    status_code=status.HTTP_200_OK,
)
async def get_employees_number(session: DatabaseSession) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_employees_number_core(session=session),
    }
