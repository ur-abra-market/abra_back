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
    # there we will ask a type of user (sellers, suppliers or admins)
    return 'Register page'


@users.get("/register/sellers")
async def register_seller():
    #tmp
    random_num = randint(0, 100000)
    result = await c.register_user(
                    user_type='sellers',
                    first_name='first_name', 
                    last_name='last_name', 
                    phone_number='phone_number', 
                    email=f'email{random_num}', 
                    password='password'
                    )
    if result:
        return 'Registration successfull!'
    elif result == 1:
        return 'User with such email not found.'
    elif result == 2:
        return 'Incorrect password.'


@users.get("/register/suppliers")
async def register_supplier():
    #tmp
    random_num = randint(0, 100000)
    result = await c.register_user(
                    user_type='suppliers',
                    first_name='first_name', 
                    last_name='last_name', 
                    phone_number='phone_number', 
                    email=f'email{random_num}', 
                    password='password'
                    )
    if result:
        return 'Registration successfull!'
    elif result == 1:
        return 'User with such email not found.'
    elif result == 2:
        return 'Incorrect password.'


@users.get("/register/admins")
async def register_admin():
    #tmp
    random_num = randint(0, 100000)
    result = await c.register_user(
                    user_type='admins',
                    first_name='first_name', 
                    last_name='last_name', 
                    phone_number='phone_number', 
                    email=f'email{random_num}', 
                    password='password'
                    )
    if result:
        return 'Registration successfull!'
    elif result == 1:
        return 'User with such email not found.'
    elif result == 2:
        return 'Incorrect password.'


@users.get("/login")
async def login_user():
    # there we will ask a type of user (sellers, suppliers or admins)
    return 'Login page'


@users.get("/login/sellers")
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


@users.get("/login/suppliers")
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


@users.get("/login/admins")
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