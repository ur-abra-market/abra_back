from typing import List

from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.depends import DatabaseSession, SupplierAuthorization, supplier
from orm import CategoryModel, ProductModel
from schemas import ApplicationResponse, Category
from typing_ import RouteReturnT

router = APIRouter(dependencies=[Depends(supplier)])


async def get_supplier_categories_core(
    supplier_id: int,
    session: AsyncSession,
) -> List[CategoryModel]:
    categories: List[CategoryModel] = (
        (
            await session.execute(
                select(CategoryModel)
                .where(
                    ProductModel.supplier_id == supplier_id,
                )
                .join(CategoryModel.products)
            )
        )
        .scalars()
        .unique()
        .all()
    )

    return categories


@router.get(
    path="",
    summary="WORKS: Get all categories from supplier products",
    response_model=ApplicationResponse[List[Category]],
    status_code=status.HTTP_200_OK,
)
async def get_supplier_categories(
    user: SupplierAuthorization,
    session: DatabaseSession,
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_supplier_categories_core(
            supplier_id=user.supplier.id,
            session=session,
        ),
    }
