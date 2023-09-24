from fastapi import APIRouter
from starlette import status

from core.depends import SupplierAuthorization
from schemas import (
    ApplicationResponse,
)
from typing_ import RouteReturnT

router = APIRouter()


@router.get(
    path="/hasBusinessInfo",
    summary="WORKS: get Company info",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
def has_business_info(user: SupplierAuthorization) -> RouteReturnT:
    return {"ok": True, "result": bool(user.supplier.company)}


@router.get(
    path="/hasPersonalInfo",
    summary="WORKS: get Personal info",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
def has_personal_info(user: SupplierAuthorization) -> RouteReturnT:
    return {"ok": True, "result": bool(user.first_name)}
