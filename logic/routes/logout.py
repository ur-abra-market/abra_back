from fastapi import APIRouter, Depends
from classes.response_models import *
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse


logout = APIRouter()


@logout.delete('/', summary='WORKS: User logout (token removal).',
              response_model=ResultOut)
async def logout_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    response = JSONResponse(
            status_code=200,
            content={"result": "User logout successfully!"}
        )
    response.delete_cookie('access_token_cookie')
    response.delete_cookie('refresh_token_cookie')
    return response
    