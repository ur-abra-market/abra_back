from fastapi import APIRouter, Depends
from .. import controller as c
from classes.response_models import *
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse
from const.const import *


login = APIRouter()


@login.post("/", summary='WORKS: User login (token creation).',
            response_model=ResultOut, responses={404: {"model": ResultOut}})
async def login_user(user_data: LoginIn,
                     Authorize: AuthJWT = Depends()):
    access_token = Authorize.create_access_token(subject=user_data.username)
    refresh_token = Authorize.create_refresh_token(subject=user_data.username)
    response = await c.login_user(user_data=user_data)
    Authorize.set_access_cookies(encoded_access_token=access_token,
                                 response=response,
                                 max_age=ACCESS_TOKEN_EXPIRATION_TIME)
    Authorize.set_refresh_cookies(encoded_refresh_token=refresh_token,
                                  response=response,
                                  max_age=REFRESH_TOKEN_EXPIRATION_TIME)
    return response


@login.post("/refresh", summary='WORKS (need csrf_refresh_token in headers): Refresh all tokens.')
def refresh_JWT_tokens(Authorize: AuthJWT = Depends()):
    Authorize.jwt_refresh_token_required()
    subject = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=subject)
    new_refresh_token = Authorize.create_refresh_token(subject=subject)
    response = JSONResponse(
                status_code=200,
                content={"result": "Access and refresh tokens were successfully updated."}
            )
    Authorize.set_access_cookies(encoded_access_token=new_access_token,
                                 response=response,
                                 max_age=ACCESS_TOKEN_EXPIRATION_TIME)
    Authorize.set_refresh_cookies(encoded_refresh_token=new_refresh_token,
                                  response=response,
                                  max_age=REFRESH_TOKEN_EXPIRATION_TIME)
    return response
                                