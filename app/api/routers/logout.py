from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse
from app.classes.response_models import ResultOut


logout = APIRouter()


@logout.delete(
    "/",
    summary="WORKS (need X-CSRF-TOKEN in headers): " "User logout (token removal).",
    response_model=ResultOut,
)
async def logout_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    response = JSONResponse(
        status_code=status.HTTP_200_OK, content={"result": "LOGOUT_SUCCESSFUL"}
    )
    Authorize.unset_jwt_cookies(response=response)
    return response
