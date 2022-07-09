from fastapi import APIRouter, Depends
from classes.response_models import *
from ..dependencies import get_current_user


me = APIRouter()


@me.get('/', summary='Get email if you authorized (TOKEN)', response_model=MyEmail)
async def get_me(user: MyEmail = Depends(get_current_user)):
    return user
