from fastapi import APIRouter
from .. import controller as c
from pydantic import BaseModel, EmailStr
from typing import Union
from classes.enums import *


register = APIRouter()

class RegisterIn(BaseModel):
    first_name: str
    last_name: str
    phone_number: Union[str, None] = None
    email: EmailStr
    password: str


class RegisterOut(BaseModel):
    result: str


@register.get("/")
async def register_main():
    # there we will ask a type of user (sellers, suppliers or admins)
    return 'Register page'


@register.post("/{user_type}/", response_model=RegisterOut)
async def register_user(user_type: str, user_data: RegisterIn):
    result = await c.register_user(user_type, user_data)
    if result == RegisterResponse.OK:
        return dict(
            result='Registration successfull!'
        )
    elif result == RegisterResponse.INCORRECT_USER_TYPE:
        return dict(
            result='Such user_type doesn\'t exist.'
        )
