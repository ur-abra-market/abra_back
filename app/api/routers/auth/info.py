from fastapi import APIRouter
from starlette import status

from core.depends import Authorization
from enums import UserType
from schemas import ApplicationResponse, User
from typing_ import RouteReturnT

router = APIRouter()


@router.get(
    path="/current",
    description="Not part of service!",
    summary="WORKS: Return a current user.",
    response_model=ApplicationResponse[User],
    status_code=status.HTTP_200_OK,
)
async def current(user: Authorization) -> RouteReturnT:
    if user.supplier:
        return {
            "ok": True,
            "result": user,
            "detail": {
                "has_profile": bool(user.supplier.company),
            },
        }

    return {
        "ok": True,
        "result": user,
    }


@router.get(
    path="/role",
    summary="WORKS: Return a current user role.",
    response_model=ApplicationResponse[UserType],
    status_code=status.HTTP_200_OK,
)
async def get_user_role(user: Authorization) -> RouteReturnT:
    return {
        "ok": True,
        "result": UserType.SUPPLIER if user.is_supplier else UserType.SELLER,
    }
