from fastapi import APIRouter
from .. import controller as c
from classes.enums import *
from classes.response_models import *


register = APIRouter()


@register.get("/")
async def register_main():
    # there we will ask a type of user (sellers, suppliers)
    return 'Register page'


@register.post("/{user_type}/", response_model=RegisterOut)
async def register_user(user_type: str, user_data: RegisterIn):
    result = await c.register_user(user_type=user_type, user_data=user_data)
    return result
