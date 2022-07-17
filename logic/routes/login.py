from fastapi import APIRouter, Depends
from .. import controller as c
from classes.response_models import *
from fastapi_jwt_auth import AuthJWT


login = APIRouter()


@login.post("/", summary='WORKS: User login (token creation).',
            response_model=ResultOut, responses={404: {"model": ResultOut}})
async def login_user(user_data: LoginIn, Authorize: AuthJWT = Depends()):
    access_token = Authorize.create_access_token(subject=user_data.username)
    refresh_token = Authorize.create_refresh_token(subject=user_data.username)
    response = await c.login_user(user_data=user_data)
    response.set_cookie('access_token_cookie', access_token)
    response.set_cookie('refresh_token_cookie', refresh_token)
    return response
