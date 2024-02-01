from typing import List

from corecrud import SelectFrom, Where
from fastapi import APIRouter
from fastapi.param_functions import Depends, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import join, joinedload, selectinload
from starlette import status

from core.app import crud
from core.depends import DatabaseSession, supplier
from orm import (
    CategoryModel,
    CategoryToPropertyTypeModel,
    CategoryToVariationTypeModel,
    PropertyValueModel,
    VariationTypeModel,
)
from schemas import ApplicationResponse, Category, PropertyValue, VariationType
from typing_ import RouteReturnT

router = APIRouter()


async def get_category_properties_core(
    session: AsyncSession, category_id: int
) -> List[PropertyValue]:
    return await crud.categories_property_values.select.many(
        Where(CategoryToPropertyTypeModel.category_id == category_id),
        SelectFrom(
            join(
                PropertyValueModel,
                CategoryToPropertyTypeModel,
                PropertyValueModel.property_type_id
                == CategoryToPropertyTypeModel.property_type_id,
            )
        ),
        session=session,
    )


@router.get(
    path="/{category_id}/properties",
    dependencies=[Depends(supplier)],
    summary="WORKS: Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[PropertyValue]],
    status_code=status.HTTP_200_OK,
)
async def get_category_properties(
    session: DatabaseSession,
    category_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_category_properties_core(session=session, category_id=category_id),
    }


async def get_product_category_variations_core(
    session: AsyncSession, category_id: int
) -> List[VariationTypeModel]:
    query = (
        select(VariationTypeModel)
        .join(CategoryToVariationTypeModel)
        .where(CategoryToVariationTypeModel.category_id == category_id)
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
