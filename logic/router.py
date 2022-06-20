from fastapi import FastAPI
import logic.controller as c
from .routes.users import users


app = FastAPI()


@app.get("/")
async def root():
    return "ok"


app.include_router(users, prefix="/users")
