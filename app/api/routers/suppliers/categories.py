from typing import List, Sequence

from fastapi import APIRouter
from fastapi.param_functions import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased
from starlette import status

from core.depends import DatabaseSession, SupplierAuthorization, supplier
from orm import CategoryModel, ProductModel
from schemas import ApplicationResponse, CategoryParent
from typing_ import RouteReturnT

router = APIRouter(dependencies=[Depends(supplier)])


async def get_supplier_categories_core(
    supplier_id: int,
    session: AsyncSession,
) -> Sequence[CategoryModel]:
    category_model_children = aliased(CategoryModel)
    category_model_grant_children = aliased(CategoryModel)

    categories: Sequence[CategoryModel] = (
        (
            await session.execute(
                select(CategoryModel)
                .join(CategoryModel.children.of_type(category_model_children))
                .join(category_model_children.children.of_type(category_model_grant_children))
                .join(
                    category_model_grant_children.products.and_(
                        ProductModel.supplier_id == supplier_id
                    )
                )
                .distinct()
            )
        )
        .scalars()
        .all()
    )
    return categories


@router.get(
    path="",
    summary="WORKS: Get all categories from supplier products",
    response_model=ApplicationResponse[List[CategoryParent]],
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
