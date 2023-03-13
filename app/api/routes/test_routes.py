from fastapi import APIRouter, Depends

from app.services import auth_service
from app.repositories import product_repo, user_repo
from app.schemas import UserSchema
from app.schemas.response_schemas import (
    ListOfProducts,
)
from app.database import get_session


test_router = APIRouter()

@test_router.get('/test_get_not_existing_user')
async def test_error(session=Depends(get_session)):
    """
    ошибки из app.api.common.exceptions можно рейзить в любом месте кода.
    их отловит и отобразит в json exception handler 
    """
    res = await user_repo.get_user_by_email(email='aa', session=session)
    return res


@test_router.get("/test_suppler_products", response_model=ListOfProducts)
async def test(user: UserSchema = Depends(auth_service.auth_optional), session=Depends(get_session)):
    products = await product_repo.get_suppliers_products(supplier_id=user.supplier_id, session=session)
    return products


@test_router.get("/test_auth_optional")
async def test_auth_optional(user: UserSchema = Depends(auth_service.auth_optional)):
    """
    auth_optional вернет app.schemas.UserSchema если юзер залогинен, 
    если нет - вернет None
    """
    return user or 'unknown user'


@test_router.get("/test_auth_required")
async def test_auth_required(user: UserSchema = Depends(auth_service.auth_required)):
    """auth_required вернет ошибку, если юзер не залогинен."""
    return user

