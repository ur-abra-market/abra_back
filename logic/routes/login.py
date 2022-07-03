from fastapi import APIRouter
from .. import controller as c
from classes.enums import *
from classes.response_models import *


login = APIRouter()


@login.post("/", response_model=LoginOut)
async def login_user(user_data: LoginIn):
    result = await c.login_user(user_data=user_data)
    return result


@login.post("/password/", response_model=ChangePasswordOut)
async def change_password(user_data: ChangePasswordIn):
    result = await c.change_password(user_data=user_data)
    return result