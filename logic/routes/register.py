from fastapi import APIRouter
from .. import controller as c
from random import randint
from pydantic import BaseModel, EmailStr
from typing import Union


register = APIRouter()

class UserIn(BaseModel):
    first_name: str
    last_name: str
    phone_number: Union[str, None] = None
    email: EmailStr
    password: str


class UserOut(BaseModel):
    result: str


@register.get("/")
async def register_main():
    # there we will ask a type of user (sellers, suppliers or admins)
    return 'Register page'


@register.post("/sellers", response_model=UserOut)
async def register_seller(user_data=UserIn):
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
        return dict(
            result='Registration successfull!'
        )
    elif result == 1:
        return dict(
            result='User with such email not found.'
        )
    elif result == 2:
        return dict(
            result='Incorrect password.'
        )

'''
@register.post("/suppliers")
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


@register.post("/admins")
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
'''