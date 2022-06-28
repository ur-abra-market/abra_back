from fastapi import APIRouter
from .. import controller as c
from classes.enums import *
from classes.response_models import *


login = APIRouter()


@login.get("/")
async def login_main():
    # there we will ask a type of user (sellers, suppliers)
    return 'Login page'


@login.post("/{user_type}/", response_model=LoginOut)
async def login_user(user_type: str, user_data: LoginIn):
    result = await c.login_user(user_type=user_type, user_data=user_data)
    return result


@login.post("/{user_type}/password/", response_model=PasswordOut)
async def login_user(user_type: str, user_data: PasswordIn):
    result = await c.update_password(user_type=user_type, user_data=user_data)
    return result