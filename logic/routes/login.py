from fastapi import APIRouter, Depends
from .. import controller as c
from classes.enums import *
from classes.response_models import *
from fastapi.security import OAuth2PasswordRequestForm
from ..dependencies import get_current_user


login = APIRouter()


@login.post("/", summary='For login use "Authorize" button in the upper right corner',
            response_model=LoginOut, responses={404: {"model": LoginError}})
async def login_user(user_data: OAuth2PasswordRequestForm = Depends()):
    result = await c.login_user(user_data=user_data)
    return result


@login.post("/password/", response_model=ChangePasswordOut)
async def change_password(user_data: ChangePasswordIn,
                          user: MyEmail = Depends(get_current_user)):
    result = await c.change_password(user_data=user_data,
                                     user_email=user.email)
    return result


@login.post("/forgot-password/")
async def forgot_password(email: MyEmail):
    result = await c.reset_password(email)
    return result