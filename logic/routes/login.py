from fastapi import APIRouter
from .. import controller as c
from random import randint
from pydantic import BaseModel, EmailStr
from classes.enums import *


login = APIRouter()

class LoginIn(BaseModel):
    email: EmailStr
    password: str


class LoginOut(BaseModel):
    result: str


@login.get("/")
async def login_main():
    # there we will ask a type of user (sellers, suppliers or admins)
    return 'Login page'


@login.post("/{user_type}/", response_model=LoginOut)
async def login_user(user_type: str, user_data: LoginIn):
    result = await c.login_user(user_type, user_data)
    if result['response'] == LoginResponse.OK:
        return dict(
            result=f'Hi, {result["first_name"]}!'
        )
    elif result['response'] == LoginResponse.USER_NOT_FOUND:
        return dict(
            result=f'User with this {user_data.email} not found.'
        )
    elif result['response'] == LoginResponse.INCORRECT_PASSWORD:
        return dict(
            result=f'Incorrect password for {user_data.email}'
        )
