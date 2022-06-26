from fastapi import APIRouter
from .. import controller as c
from classes.enums import *
from classes.response_models import *


login = APIRouter()


@login.get("/")
async def login_main():
    # there we will ask a type of user (sellers, suppliers or admins)
    return 'Login page'


@login.post("/{user_type}/", response_model=LoginOut)
async def login_user(user_type: str, user_data: LoginIn):
    if user_type not in ['sellers', 'suppliers', 'admins']:
        return dict(
            result='404: PAGE NOT FOUND (incorrect subdomain)'
        ) 

    result = await c.login_user(user_type, user_data)
    if result['response'] == LoginResponse.OK:
        return dict(
            result=f'Login successfull. Hi, {result["first_name"]}!'
        )
    elif result['response'] == LoginResponse.USER_NOT_FOUND:
        return dict(
            result=f'User {user_data.email} not found.'
        )
    elif result['response'] == LoginResponse.INCORRECT_PASSWORD:
        return dict(
            result=f'Incorrect password for {user_data.email}'
        )



@login.post("/{user_type}/password/", response_model=PasswordOut)
async def login_user(user_type: str, user_data: PasswordIn):
    if user_type not in ['sellers', 'suppliers', 'admins']:
        return dict(
            result='404: PAGE NOT FOUND (incorrect subdomain)'
        ) 

    result = await c.update_password(user_type, user_data)
    if result == PasswordUpdatingResponse.OK:
        return dict(
            result=f'Password for user {user_data.email} successfully updated!'
        )
    elif result == PasswordUpdatingResponse.USER_NOT_FOUND:
        return dict(
            result=f'User {user_data.email} not found.'
        )
    elif result == PasswordUpdatingResponse.INCORRECT_PASSWORD:
        return dict(
            result=f'Incorrect old password for {user_data.email}'
        )