from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from os import getenv
import logging
from logic.routes import suppliers
from .routes import *
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from classes.response_models import *
from fastapi_jwt_auth.exceptions import AuthJWTException

logging.basicConfig(level=logging.INFO)

DEBUG = bool(int(getenv("DEBUG", 0)))

app = FastAPI(
    title="wb_platform",
    description="API for wb_platform.",
    version="0.0.1",
    debug=DEBUG
)

if DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],
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
        content={"detail": exc.message}
    )


@app.get("/")
async def get():
    return "Ok!"


@app.post("/")
async def post():
    return "Ok!"


app.include_router(login.login, tags=["login"], prefix="/login")
app.include_router(logout.logout, tags=["logout"], prefix="/logout")
app.include_router(password.password, tags=["password"], prefix="/password")
app.include_router(register.register, tags=["register"], prefix="/register")
app.include_router(users.users, tags=["users"], prefix="/users")
app.include_router(products.products, tags=["products"], prefix="/products")
app.include_router(categories.categories, tags=["categories"], prefix="/categories")
app.include_router(suppliers.suppliers, tags=["suppliers"], prefix="/suppliers")
app.include_router(reviews.reviews, tags=["reviews"], prefix="/reviews")
