from typing import List

from corecrud import Options, SelectFrom, Where
from fastapi import APIRouter
from fastapi.param_functions import Depends, Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import join, selectinload
from starlette import status

from core.app import crud
from core.depends import DatabaseSession, supplier
from orm import (
    CategoryModel,
    CategoryToPropertyTypeModel,
    CategoryToVariationTypeModel,
    PropertyValueModel,
    VariationTypeModel,
    VariationValueModel,
)
from schemas import ApplicationResponse, Category, PropertyValue, VariationValue
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


async def get_category_variations_core(
    session: AsyncSession, category_id: int
) -> List[VariationValue]:
    return await crud.categories_variation_values.select.many(
        Where(CategoryToVariationTypeModel.category_id == category_id),
        Options(
            selectinload(VariationValueModel.type),
        ),
        SelectFrom(
            join(
                CategoryToVariationTypeModel,
                VariationTypeModel,
                CategoryToVariationTypeModel.variation_type_id == VariationTypeModel.id,
            )
        ),
        session=session,
    )


@router.get(
    path="/{category_id}/variations",
    dependencies=[Depends(supplier)],
    summary="WORKS (ex. 1): Get all variation names and values by category_id.",
    response_model=ApplicationResponse[List[VariationValue]],
    status_code=status.HTTP_200_OK,
)
async def get_category_variations(
    session: DatabaseSession,
    category_id: int = Path(...),
) -> RouteReturnT:
    return {
        "ok": True,
        "result": await get_category_variations_core(session=session, category_id=category_id),
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
