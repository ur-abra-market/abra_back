from fastapi import APIRouter, Depends, Request
from .. import controller as c
from classes.response_models import *
from fastapi_jwt_auth import AuthJWT


password = APIRouter()


@password.post("/change/", 
               summary='WORKS (need csrf_access_token in headers): Change password (token is needed).',
               response_model=ResultOut, responses={404: {"model": ResultOut}})
async def change_password(user_data: ChangePasswordIn,
                          Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    result = await c.change_password(user_data=user_data,
                                     user_email=user_email)
    return result


@password.post("/forgot-password/",
               summary='WORKS: Send letter with link (token) to user email. Next step is /sheck-for token.',
               response_model=ResultOut)
async def forgot_password(email: MyEmail):
    result = await c.send_reset_message(email.email)
    return result


@password.post("/check-for-token/",
               summary="WORKS: Receive and check token. Next step is /reset-password.",
               response_model=ResultOut)
async def check_for_token(token: str):
    result = await c.check_token(token)
    return result


@password.patch("/reset-password/",
                summary='WORKS: reset and change password.',
                response_model=ResultOut)
async def reset_password(user_data: ResetPassword):
    result = await c.reset_user_password(user_email=user_data.email,
                                user_new_password=user_data.new_password,
                                user_confirm_new_password=user_data.confirm_password)
    return result
