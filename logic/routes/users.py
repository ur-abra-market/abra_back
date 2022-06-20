from fastapi import APIRouter
from .. import controller as c
from random import randint


users = APIRouter()

@users.get("/")
async def get_users():
    result = await c.get_users()
    return result



@users.get("/register")
async def register_user():
    #tmp
    random_num = randint(0, 100000)
    result = await c.register_user(
                    first_name='first_name', 
                    last_name='last_name', 
                    phone_number='phone_number', 
                    email=f'email{random_num}', 
                    password='password'
                    )
    if result:
        return 'Registration successfull!'
    else:
        return 'Registration failed..'


@users.get("/login")
async def login_user():
    username = await c.login_user(
                    email='email', 
                    password='password'
                    )
    if username:
        return f'Hi, {username["first_name"]} {username["last_name"]}!'
    else:
        return 'Email or password incorrect!'