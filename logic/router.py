from fastapi import FastAPI
import logic.controller as c
from .routes.login import login
from .routes.register import register


app = FastAPI(
    title="wb_platform",
    description="API for wb_platform.",
    version="0.0.1"
)


@app.get("/")
async def root():
    return "This is root"


app.include_router(login, prefix="/login")
app.include_router(register, prefix="/register")
