from fastapi import APIRouter, Depends
from .. import controller as c
from classes.response_models import *
from fastapi_jwt_auth import AuthJWT
from logic.consts import *


users = APIRouter()


@users.get("/latest_searches/", summary='WORKS (example 83): Get latest searches by user_id.',
              response_model=SearchesOut)
async def get_latest_searches_for_user(user_id: int):
    result = await c.get_latest_searches_for_user(user_id=user_id)
    return result
