from fastapi import APIRouter, Depends
from .. import controller as c
from classes.enums import *
from classes.response_models import *
from fastapi.security import OAuth2PasswordRequestForm


login = APIRouter()


@login.post("/", response_model=LoginOut, responses={404: {"model": LoginError}})
async def login_user(user_data: OAuth2PasswordRequestForm = Depends()):
    result = await c.login_user(user_data=user_data)
    return result


@login.post("/password/", response_model=ChangePasswordOut)
async def change_password(user_data: ChangePasswordIn):
    result = await c.change_password(user_data=user_data)
    return result