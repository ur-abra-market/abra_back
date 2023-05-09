from fastapi import APIRouter
from fastapi.param_functions import Depends
from fastapi.responses import Response
from starlette import status

from core.depends import AuthJWT, authorization, unset_jwt_cookies
from schemas import ApplicationResponse
from typing_ import RouteReturnT

router = APIRouter()


@router.delete(
    path="/",
    dependencies=[Depends(authorization)],
    summary="WORKS (need X-CSRF-TOKEN in headers): User logout (token removal).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def logout_user(
    response: Response,
    authorize: AuthJWT,
) -> RouteReturnT:
    unset_jwt_cookies(response=response, authorize=authorize)

    return {
        "ok": True,
        "result": True,
    }
