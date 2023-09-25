from fastapi import APIRouter, Depends
from fastapi.responses import Response
from starlette import status

from core.depends import (
    AuthJWT,
    authorization,
)
from schemas import ApplicationResponse
from typing_ import RouteReturnT
from utils.cookies import unset_jwt_cookies

router = APIRouter()


@router.delete(
    path="/",
    dependencies=[Depends(authorization)],
    summary="WORKS (need X-CSRF-TOKEN in headers): User logout (token removal).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def sign_out(
    response: Response,
    authorize: AuthJWT,
) -> RouteReturnT:
    unset_jwt_cookies(response=response, authorize=authorize)

    return {
        "ok": True,
        "result": True,
    }
