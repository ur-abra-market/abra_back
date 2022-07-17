from fastapi import APIRouter, Depends
from .. import controller as c
from classes.response_models import *
from fastapi.security import OAuth2PasswordRequestForm
from ..dependencies import get_current_user


login = APIRouter()


@login.post("/password/", summary='WORKS: Change password.', 
            response_model=ChangePasswordOut)
async def change_password(user_data: ChangePasswordIn,
                          user: MyEmail = Depends(get_current_user)):
    result = await c.change_password(user_data=user_data,
                                     user_email=user.email)
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


@login.post("/", summary='For login use "Authorize" button in the upper right corner',
            response_model=LoginOut, responses={404: {"model": LoginError}})
async def login_user(user_data: OAuth2PasswordRequestForm = Depends()):
    result = await c.login_user(user_data=user_data)
    return result