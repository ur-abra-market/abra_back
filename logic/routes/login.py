from fastapi import APIRouter
from .. import controller as c
from random import randint
from pydantic import BaseModel, EmailStr


login = APIRouter()


@login.get("/")
async def login_main():
    # there we will ask a type of user (sellers, suppliers or admins)
    return 'Login page'


@login.post("/sellers")
async def login_seller():
    username = await c.login_user(
                    user_type='sellers',
                    email='email', 
                    password='password'
                    )
    if username:
        return f'Hi, {username["first_name"]} {username["last_name"]}!'
    else:
        return 'Email or password incorrect!'

'''
@login.post("/suppliers")
async def login_supplier():
    username = await c.login_user(
                    user_type='suppliers',
                    email='email', 
                    password='password'
                    )
    if username:
        return f'Hi, {username["first_name"]} {username["last_name"]}!'
    else:
        return 'Email or password incorrect!'


@login.post("/admins")
async def login_admin():
    username = await c.login_user(
                    user_type='admins',
                    email='email', 
                    password='password'
                    )
    if username:
        return f'Hi, {username["first_name"]} {username["last_name"]}!'
    else:
        return 'Email or password incorrect!'
        '''