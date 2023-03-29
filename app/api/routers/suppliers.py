from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, join
from starlette import status

from core.depends import UserObjects, auth_required, get_session
from core.tools import store
from orm import (
    UserModel,
    CompanyModel,
    SupplierModel,
    ProductModel,
)

from schemas import (
    ApplicationResponse,
    SuppliersProductsResponse,
)

router = APIRouter()


@router.get("/get_supplier_info")
async def get_supplier_info(
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
):

    await store.orm.users.get_one(
        SupplierModel,
        CompanyModel,
        session=session,
        where=[UserModel.id == user.schema.id],
        join=[
            [SupplierModel, SupplierModel.user_id == UserModel.id],
            [CompanyModel, CompanyModel.supplier_id == SupplierModel.id],
        ],
        options=[joinedload(UserModel.supplier.company)]
        # select_from=[
        #   join(CompanyModel, SupplierModel, CompanyModel.supplier_id == SupplierModel.id)
        # ]
    )
    return {"ok": False, "result": "Not working yet..."}


@router.get(
    path="/manage_products",
    summary="WORKS: update seller data",
    status_code=status.HTTP_200_OK,
    # response_class=ApplicationResponse[SuppliersProductsResponse],
    # FIXME:L чет падает с TypeError: __init__() takes exactly 1 positional argument (2 given)
)
async def manage_products(
    user: UserObjects = Depends(auth_required),
    session: AsyncSession = Depends(get_session),
) -> ApplicationResponse[SuppliersProductsResponse]:
    # TODO: pagination?
    res = await store.orm.suppliers.get_one(
        ProductModel,
        session=session,
        where=[UserModel.id == user.schema.id],
        options=[
            joinedload(SupplierModel.products),
        ],
    )
    return {"ok": True, "result": {"supplier": res}}
