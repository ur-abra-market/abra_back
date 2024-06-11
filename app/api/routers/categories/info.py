from typing import List

from corecrud import SelectFrom, Where
from fastapi import APIRouter
from fastapi.param_functions import Depends, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import join, joinedload, selectinload, raiseload, aliased
from starlette import status

from core import exceptions
from core.app import crud
from core.depends import DatabaseSession, supplier
from orm import (
    CategoryModel,
    CategoryToPropertyTypeModel,
    PropertyValueModel,
    CategoryToVariationTypeModel,
    PropertyTypeModel,
    VariationTypeModel,
)
from schemas import ApplicationResponse, Category, PropertyType, PropertyValue, VariationType, VariationValue
from typing_ import RouteReturnT

router = APIRouter()


async def get_product_category_properties_core(
    session: AsyncSession, category_id: int
) -> List[PropertyTypeModel]:
    query = (
        select(PropertyTypeModel)
        .join(PropertyTypeModel.category)
        .where(CategoryModel.id == category_id)
        .options(joinedload(PropertyTypeModel.values))
    )
    result = await session.execute(query)
    return result.unique().scalars().all()


@router.get(
    path="/{category_id}/properties",
    summary="WORKS: Get all property names and values by category_id.",
    response_model=ApplicationResponse[List[PropertyType]],
    status_code=status.HTTP_200_OK,
)
async def get_product_category_properties(
    session: DatabaseSession,
    category_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_product_category_properties_core(
            session=session, category_id=category_id
        ),
    }


async def get_product_category_variations_core(
    session: AsyncSession, category_id: int
) -> List[VariationTypeModel]:
    query = (
        select(VariationTypeModel)
        .join(VariationTypeModel.category)
        .where(CategoryModel.id == category_id)
        .options(joinedload(VariationTypeModel.values))
    )
    result = await session.execute(query)
    return result.unique().scalars().all()


@router.get(
    path="/{category_id}/variations",
    summary="WORKS: Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[VariationType]],
    status_code=status.HTTP_200_OK,
)
async def get_product_category_variations(
    session: DatabaseSession,
    category_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_product_category_variations_core(
            session=session, category_id=category_id
        ),
    }


async def get_category_parents_core(
    session: AsyncSession, category_id: int
) -> List[CategoryModel]:
    cte = (
        select(CategoryModel.id, CategoryModel.parent_id, CategoryModel.level)
        .where(CategoryModel.id == category_id)
        .cte(name="parents", recursive=True)
    )
    parent_alias = aliased(CategoryModel, name="parent")
    cte = cte.union_all(
        select(parent_alias.id, parent_alias.parent_id, parent_alias.level).where(
            parent_alias.id == cte.c.parent_id
        )
    )
    query = (
        select(CategoryModel)
        .join(cte, CategoryModel.id == cte.c.id)
        .options(raiseload("*"))
        .order_by(CategoryModel.level)
    )
    result_nodes = await session.execute(query)
    return result_nodes.scalars().all()


@router.get(
    path="/{category_id}/breadcrumbs",
    summary="WORKS: Get all parent categories by category_id, sorted asc by level.",
    response_model=ApplicationResponse[List[Category]],
    status_code=status.HTTP_200_OK,
)
async def get_category_breadcrumbs(
    session: DatabaseSession, category_id: int = Path(...)
) -> RouteReturnT:
    data = await get_category_parents_core(session=session, category_id=category_id)
    if not data:
        raise exceptions.NotFoundException(detail="Category not found")
    return {"ok": True, "result": data}


async def get_all_categories_core(session: AsyncSession) -> List[CategoryModel]:
    return (
        (
            await session.execute(
                select(CategoryModel)
                .where(CategoryModel.level == 1)
                .options(selectinload(CategoryModel.children).selectinload(CategoryModel.children))
            )
        )
        .scalars()
        .all()
    )


@router.get(
    path="/all",
    summary="WORKS: Get all categories.",
    response_model=ApplicationResponse[List[Category]],
    status_code=status.HTTP_200_OK,
)
async def get_all_categories(session: DatabaseSession) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_all_categories_core(session=session),
    }
