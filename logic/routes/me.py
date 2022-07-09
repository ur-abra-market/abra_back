from fastapi import APIRouter, Depends
from classes.response_models import *
from ..dependencies import get_current_user


me = APIRouter()


@me.get('/', summary='Get details of currently logged in user', response_model=SystemUser)
async def get_me(user: SystemUser = Depends(get_current_user)):
    return user
