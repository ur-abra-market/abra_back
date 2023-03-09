from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import colorlog

from app.logic.routes import (
    login,
    logout,
    password,
    register,
    users,
    products,
    categories,
    suppliers,
    reviews,
    sellers,
)
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from app.classes.response_models import Settings
from fastapi_jwt_auth.exceptions import AuthJWTException
from app.settings import DEBUG, DOCS_URL, REDOC_URL, OPENAPI_URL, ALLOW_ORIGINS


app = FastAPI(
    title="wb_platform",
    description="API for wb_platform.",
    version="0.0.1",
    debug=DEBUG,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL,
)

# set up cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
    allow_headers=["*"],
)


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.on_event("startup")
def startup():
    handler = logging.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        fmt="%(log_color)s%(levelname)s%(reset)s \t\t | %(asctime)s.%(msecs)03d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    ))

    # general logging setup
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if DEBUG else logging.ERROR)
    logger.addHandler(handler)

    # sqlalchemy logging setup
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if DEBUG else logging.ERROR
    )
    logging.getLogger("sqlalchemy.pool").setLevel(
        logging.ERROR if DEBUG else logging.ERROR
    )


@app.get("/")
async def get():
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
app.include_router(sellers.sellers, tags=["sellers"], prefix="/sellers")
