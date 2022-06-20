from fastapi import APIRouter

users = APIRouter()


@users.get("/")
async def get_users():
    result = await c.get_users()
    return result
