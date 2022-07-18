from fastapi import APIRouter, Depends
from .. import controller as c
from classes.response_models import *
from fastapi_jwt_auth import AuthJWT


password = APIRouter()


@password.post("/change/", summary='WORKS: Change password (token is needed).',
            response_model=ResultOut, responses={404: {"model": ResultOut}})
async def change_password(user_data: ChangePasswordIn,
                          Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_email = Authorize.get_jwt_subject()
    result = await c.change_password(user_data=user_data,
                                     user_email=user_email)
    return result


@password.post("/forgot-password/",
               summary='WORKS: Send letter with link (token) to user email. Next step is /reset-password.',
               response_model=ResultOut)
async def forgot_password(email: MyEmail):
    result = await c.send_reset_message(email.email)
    return result


@password.patch("/reset-password/",
                summary='WORKS (will split on two parts): Receive token that was sent using /forgot-password.',
                response_model=ResultOut)
async def reset_password(user_data: ResetPassword):
    result = await c.reset_user_password(user_email=user_data.email,
                                user_token=user_data.reset_password_token,
                                user_new_password=user_data.new_password,
                                user_confirm_new_password=user_data.confirm_password)
    return result
