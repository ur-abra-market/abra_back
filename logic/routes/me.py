from fastapi import APIRouter, Depends
from classes.response_models import *
from ..dependencies import get_current_user


# it is temporary route
me = APIRouter()


@me.get('/', summary='For testing purposes. Get email if you authorized (TOKEN)', response_model=MyEmail)
async def get_me(user: MyEmail = Depends(get_current_user)):
    return user
