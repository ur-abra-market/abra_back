from fastapi import FastAPI, Request
from .logic.controller import *


app = FastAPI()


@app.get("/")
async def root():
    return "ok"


# @app.get("/")
# async def initiliaze():
#     initiliaze()
