from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from .routes.login import login
from .routes.register import register
from .routes.me import me
from .routes.products import products
from .routes.categories import categories


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


@app.get("/")
async def root():
    return "This is root"


@app.post("/")
async def post():
    return "answer from post"


app.include_router(login, prefix="/login")
app.include_router(register, prefix="/register")
app.include_router(me, prefix="/me")
app.include_router(products, prefix="/products")
app.include_router(categories, prefix="/categories")
