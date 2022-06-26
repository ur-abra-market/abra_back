from fastapi import APIRouter
from .. import controller as c
from classes.enums import *
from classes.response_models import *

register = APIRouter()


@register.get("/")
async def register_main():
    # there we will ask a type of user (sellers, suppliers or admins)
    return 'Register page'


@register.post("/{user_type}/", response_model=RegisterOut)
async def register_user(user_type: str, user_data: RegisterIn):
    if user_type not in ['sellers', 'suppliers', 'admins']:
        return dict(
            result='404: PAGE NOT FOUND (incorrect subdomain)'
        ) 

    result = await c.register_user(user_type, user_data)
    if result == RegisterResponse.OK:
        return dict(
            result='Registration successfull!'
        )
    elif result == RegisterResponse.WRONG_DATA:
        return dict(
            result='User with such data couldn\'t be registered. '\
                   'Data don\'t fit in column in database (too long value).'
        )
    elif result == RegisterResponse.EMAIL_ALREADY_EXIST:
        return dict(
            result=f'User with {user_data.email} already exist.'
        )
