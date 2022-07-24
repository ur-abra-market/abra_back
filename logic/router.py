from fastapi import FastAPI, HTTPException, Depends, Request
from starlette.middleware.cors import CORSMiddleware
from .routes.login import login
from .routes.logout import logout
from .routes.password import password
from .routes.register import register
from .routes.products import products
from .routes.categories import categories
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from classes.response_models import *
from fastapi_jwt_auth.exceptions import AuthJWTException


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
        content={"detail": exc.message}
    )


@app.get("/")
async def get():
    return "Ok!"


@app.post("/")
async def post():
    return "Ok!"


app.include_router(login, prefix="/login")
app.include_router(logout, prefix="/logout")
app.include_router(password, prefix="/password")
app.include_router(register, prefix="/register")
app.include_router(products, prefix="/products")
app.include_router(categories, prefix="/categories")


# raise HTTPException(
#     status_code=status.HTTP_403_FORBIDDEN,
#     detail="Could not validate credentials",
# #     headers={"WWW-Authenticate": "Bearer"},
# )