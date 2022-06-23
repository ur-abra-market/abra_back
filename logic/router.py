from fastapi import FastAPI
import logic.controller as c
from .routes.login import login
from .routes.register import register


app = FastAPI()


@app.get("/")
async def root():
    return "ok"


app.include_router(login, prefix="/login")
app.include_router(register, prefix="/register")
