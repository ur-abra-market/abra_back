from fastapi import APIRouter
from .. import controller as c


users = APIRouter()

@users.get("/")
async def get_users():
    result = await c.get_users()
    return result
