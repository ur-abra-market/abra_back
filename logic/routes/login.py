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


@login.post("/password/", summary='WORKS: Change password (token is needed).',
            response_model=ResultOut, responses={404: {"model": ResultOut}})
async def change_password(user_data: ChangePasswordIn,
                          Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    result = await c.change_password(user_data=user_data,
                                     user_email=user_email)
    return result


@login.post("/forgot-password/")
async def forgot_password(email: MyEmail):
    result = await c.send_reset_message(email.email)
    return result


@login.patch("/reset-password/")
async def reset_password(user_data: ResetPassword):
    result = await c.reset_user_password(user_email=user_data.email,
                                user_token=user_data.reset_password_token,
                                user_new_password=user_data.new_password,
                                user_confirm_new_password=user_data.confirm_password)
    return result
