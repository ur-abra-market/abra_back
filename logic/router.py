from fastapi import FastAPI, HTTPException, Depends, Request
from starlette.middleware.cors import CORSMiddleware
from .routes.login import login
from .routes.logout import logout
from .routes.register import register
from .routes.products import products
from .routes.categories import categories
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from classes.response_models import *
from fastapi_jwt_auth.exceptions import AuthJWTException
from logic import controller as c


app = FastAPI(
    title="wb_platform",
    description="API for wb_platform.",
    version="0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": "User not authorised (use login)."}
    )


@app.get("/")
async def root():
    return "This is root"


@app.post("/")
async def post():
    return "answer from post"


app.include_router(login, prefix="/login")
app.include_router(logout, prefix="/logout")
app.include_router(register, prefix="/register")
app.include_router(products, prefix="/products")
app.include_router(categories, prefix="/categories")
