from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logic.controller as c
from .routes.login import login
from .routes.register import register


app = FastAPI(
    title="wb_platform",
    description="API for wb_platform.",
    version="0.0.1"
)

origins = [
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return "This is root"


app.include_router(login, prefix="/login")
app.include_router(register, prefix="/register")
