# mypy: ignore-errors

from __future__ import annotations

import csv
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Generic, List, Type, TypeVar

from pydantic import parse_obj_as

from core.app import CRUD
from core.app import crud as c
from orm.core.session import async_sessionmaker
from schemas import (
    Category,
    CategoryProperty,
    CategoryPropertyType,
    CategoryPropertyValue,
    CategoryVariation,
    CategoryVariationType,
    CategoryVariationValue,
    CompanyNumOfEmployees,
    Country,
    OrderStatus,
    ORMSchema,
)
from typing_ import DictStrAny

CSV_DIR = Path(__file__).parent / "csv"

CATEGORIES_FILE = CSV_DIR / "categories.csv"
ORDER_STATUSES_FILE = CSV_DIR / "order_statuses.csv"
CATEGORIES_PROPERTY_TYPES_FILE = CSV_DIR / "category_property_type.csv"
CATEGORIES_PROPERTY_VALUES_FILE = CSV_DIR / "category_property_value.csv"
CATEGORIES_PROPERTIES_FILE = CSV_DIR / "category_properties.csv"
CATEGORIES_VARIATION_TYPES_FILE = CSV_DIR / "category_variation_type.csv"
CATEGORIES_VARIATION_VALUES_FILE = CSV_DIR / "category_variation_value.csv"
CATEGORIES_VARIATIONS_FILE = CSV_DIR / "category_variation.csv"
COMPANY_EMPLOYEES_FILE = CSV_DIR / "company_num_of_employee.csv"
COUNTRIES_FILE = CSV_DIR / "countries.csv"

SchemaT = TypeVar("SchemaT", bound=ORMSchema)


def _csv_reader(path: Path) -> List[DictStrAny]:
    with open(path, encoding="utf-8") as f:
        _csv = [
            {k: v or None for k, v in row.items()}  # type: ignore
            for row in csv.DictReader(f=f, skipinitialspace=True)
        ]
    return _csv  # noqa


def load_from_csv(path: Path, schema_t: Type[SchemaT]) -> List[SchemaT]:
    return parse_obj_as(List[schema_t], _csv_reader(path=path))


def csv_to_pydantic(path: Path, schema_t: Type[SchemaT]) -> List[SchemaT]:
    return load_from_csv(path=path, schema_t=schema_t)


class DatabaseLoader(Generic[SchemaT]):
    def __init__(
        self,
        crud: CRUD,
        *,
        path: Path,
        schema_t: Type[SchemaT],
    ) -> None:
        self.pydantic = csv_to_pydantic(path=path, schema_t=schema_t)
        self.crud = crud

    async def load(self) -> None:
        async with async_sessionmaker.begin() as session:
            for row in self.pydantic:
                await self.crud.insert.one(session=session, values=row.dict())


@dataclass(
    repr=False,
    eq=True,
    frozen=True,
    order=True,
)
class CSVLoader:
    categories: DatabaseLoader[Category] = DatabaseLoader(
        crud=c.categories,
        path=CATEGORIES_FILE,
        schema_t=Category,
    )
    order_statuses: DatabaseLoader[OrderStatus] = DatabaseLoader(
        crud=c.orders_statuses,
        path=ORDER_STATUSES_FILE,
        schema_t=OrderStatus,
    )
    categories_property_types: DatabaseLoader[CategoryPropertyType] = DatabaseLoader(
        crud=c.categories_property_types,
        path=CATEGORIES_PROPERTY_TYPES_FILE,
        schema_t=CategoryPropertyType,
    )
    categories_property_values: DatabaseLoader[CategoryPropertyValue] = DatabaseLoader(
        crud=c.categories_property_values,
        path=CATEGORIES_PROPERTY_VALUES_FILE,
        schema_t=CategoryPropertyValue,
    )
    categories_properties: DatabaseLoader[CategoryProperty] = DatabaseLoader(
        crud=c.categories_properties, path=CATEGORIES_PROPERTIES_FILE, schema_t=CategoryProperty
    )
    categories_variation_types: DatabaseLoader[CategoryVariationType] = DatabaseLoader(
        crud=c.categories_variation_types,
        path=CATEGORIES_VARIATION_TYPES_FILE,
        schema_t=CategoryVariationType,
    )
    categories_variation_values: DatabaseLoader[CategoryVariationValue] = DatabaseLoader(
        crud=c.categories_variation_values,
        path=CATEGORIES_VARIATION_VALUES_FILE,
        schema_t=CategoryVariationValue,
    )
    categories_variations: DatabaseLoader[CategoryVariation] = DatabaseLoader(
        crud=c.categories_variations, path=CATEGORIES_VARIATIONS_FILE, schema_t=CategoryVariation
    )

    company_num_of_employee: DatabaseLoader[CompanyNumOfEmployees] = DatabaseLoader(
        crud=c.company_num_of_employees,
        path=COMPANY_EMPLOYEES_FILE,
        schema_t=CompanyNumOfEmployees,
    )

    countries: DatabaseLoader[Country] = DatabaseLoader(
        crud=c.country, path=COUNTRIES_FILE, schema_t=Country
    )

    async def setup(self) -> None:
        for field in fields(self):
            await getattr(CSVLoader, field.name).load()


csv_loader = CSVLoader()
