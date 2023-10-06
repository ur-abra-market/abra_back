# mypy: ignore-errors

from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Generic, List, Type, TypeVar

from corecrud import CRUD, Returning, Values
from pydantic import parse_obj_as

from core.app import crud
from orm.core import async_sessionmaker
from schemas import (
    Brand,
    Category,
    CategoryToPropertyType,
    CategoryToVariationType,
    Country,
    EmployeesNumber,
    ORMSchema,
    PropertyType,
    PropertyValue,
    VariationType,
    VariationValue,
)
from typing_ import DictStrAny

csv.field_size_limit(sys.maxsize)

CSV_DIR = Path(__file__).parent / "csv"

BRANDS_FILE = CSV_DIR / "brands.csv"
CATEGORIES_TO_PROPERTY_TYPES_FILE = CSV_DIR / "categories_to_property_types.csv"
CATEGORIES_TO_VARIATION_TYPES_FILE = CSV_DIR / "categories_to_variation_types.csv"
CATEGORIES_FILE = CSV_DIR / "categories.csv"
COUNTRIES_FILE = CSV_DIR / "countries.csv"
NUMBER_EMPLOYEES_FILE = CSV_DIR / "employees_number.csv"
PROPERTY_TYPES_FILE = CSV_DIR / "property_types.csv"
PROPERTY_VALUES_FILE = CSV_DIR / "property_values.csv"
# TAGS_FILE = CSV_DIR / "tags.csv"
VARIATION_TYPES_FILE = CSV_DIR / "variation_types.csv"
VARIATION_VALUES_FILE = CSV_DIR / "variation_values.csv"

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
                await self.crud.insert.one(
                    Values(row.dict()),
                    Returning(self.crud.model),
                    session=session,
                )


@dataclass(
    repr=False,
    eq=True,
    frozen=True,
    order=True,
)
class CSVLoader:
    brands: DatabaseLoader[Brand] = DatabaseLoader(
        crud=crud.brands,
        path=BRANDS_FILE,
        schema_t=Brand,
    )
    categories: DatabaseLoader[Category] = DatabaseLoader(
        crud=crud.categories,
        path=CATEGORIES_FILE,
        schema_t=Category,
    )
    categories_property_types: DatabaseLoader[PropertyType] = DatabaseLoader(
        crud=crud.property_types,
        path=PROPERTY_TYPES_FILE,
        schema_t=PropertyType,
    )
    categories_property_values: DatabaseLoader[PropertyValue] = DatabaseLoader(
        crud=crud.property_values,
        path=PROPERTY_VALUES_FILE,
        schema_t=PropertyValue,
    )
    categories_properties: DatabaseLoader[CategoryToPropertyType] = DatabaseLoader(
        crud=crud.category_to_propetry_types,
        path=CATEGORIES_TO_PROPERTY_TYPES_FILE,
        schema_t=CategoryToPropertyType,
    )
    categories_variation_types: DatabaseLoader[VariationType] = DatabaseLoader(
        crud=crud.variation_types,
        path=VARIATION_TYPES_FILE,
        schema_t=VariationType,
    )
    categories_variation_values: DatabaseLoader[VariationValue] = DatabaseLoader(
        crud=crud.variation_values,
        path=VARIATION_VALUES_FILE,
        schema_t=VariationValue,
    )
    categories_variations: DatabaseLoader[CategoryToVariationType] = DatabaseLoader(
        crud=crud.categories_to_variation_types,
        path=CATEGORIES_TO_VARIATION_TYPES_FILE,
        schema_t=CategoryToVariationType,
    )

    employees_number: DatabaseLoader[EmployeesNumber] = DatabaseLoader(
        crud=crud.employees_number,
        path=NUMBER_EMPLOYEES_FILE,
        schema_t=EmployeesNumber,
    )

    countries: DatabaseLoader[Country] = DatabaseLoader(
        crud=crud.country,
        path=COUNTRIES_FILE,
        schema_t=Country,
    )

    # tags: DatabaseLoader[Tags] = DatabaseLoader(
    #     crud=crud.tags,
    #     path=TAGS_FILE,
    #     schema_t=Tags,
    # )

    async def setup(self) -> None:
        for field in fields(self):
            await getattr(CSVLoader, field.name).load()


csv_loader = CSVLoader()
