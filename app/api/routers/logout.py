# mypy: disable-error-code="arg-type,return-value"

from fastapi import APIRouter
from fastapi.param_functions import Depends
from fastapi_jwt_auth import AuthJWT
from starlette import status

from core.depends import auth_required
from schemas import ApplicationResponse

router = APIRouter()


def unset_jwt_cookies(authorize: AuthJWT) -> None:
    authorize.unset_jwt_cookies()


@router.delete(
    path="/",
    dependencies=[Depends(auth_required)],
    summary="WORKS (need X-CSRF-TOKEN in headers): User logout (token removal).",
    response_model=ApplicationResponse[bool],
    status_code=status.HTTP_200_OK,
)
async def logout_user(authorize: AuthJWT = Depends()) -> ApplicationResponse[bool]:
    unset_jwt_cookies(authorize=authorize)

    return {
        "ok": True,
        "result": True,
    }
