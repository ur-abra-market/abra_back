from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse
from classes.response_models import *


logout = APIRouter()


@logout.delete('/',
               summary='WORKS (need csrf_access_token in headers): '
                       'User logout (token removal).',
               response_model=ResultOut)
async def logout_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    response = JSONResponse(
        status_code=200,
        content={"result": "LOGOUT_SUCCESSFUL"}
    )
    Authorize.unset_jwt_cookies(response=response)
    return response
