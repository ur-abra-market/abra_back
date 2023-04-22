# mypy: ignore-errors
import asyncio
import csv
from pathlib import Path
from typing import Any, List, Type
from uuid import UUID

from loguru import logger

from core.app import crud
from orm.core.session import async_sessionmaker
from schemas import (
    Category,
    Company,
    Product,
    OrderStatus,
    CategoryVariation,
    CategoryPropertyType,
    CategoryPropertyValue,
    CategoryProperty,
    CategoryVariationType,
    CategoryVariationValue,
    OrderProductVariation,
)
from schemas.orm.core import ORMSchema
from core.app.crud import CRUD


DATA_DIR = Path("app/population/data")

CATEGORIES_FILE = DATA_DIR / "categories.csv"
ORDER_STATUSES_FILE = DATA_DIR / "order_stasuses.csv"
CAT_PROP_TYPE_FILE = DATA_DIR / "category_property_type.csv"
CAT_PROP_VAL_FILE = DATA_DIR / "category_property_value.csv"
CAT_PROP_FILE = DATA_DIR / "category_properties.csv"
CAT_VAR_TYPE_FILE = DATA_DIR / "category_variation_type.csv"
CAT_VAR_VAL_FILE = DATA_DIR / "category_variation_value.csv"
CAT_VAR_FILE = DATA_DIR / "category_variation.csv"
ORDER_PRODUCT_VAR_FILE = DATA_DIR / "order_product_variarion.csv"


class UploadProduct(Product):
    category_id: int
    supplier_id: int


class UploadCompany(Company):
    supplier_id: int


class UploadOrderProductVariation(OrderProductVariation):
    order_id: int
    status_id: int


class LoadFromFile:
    """Loads constants (categories, property values) from file"""

    def __init__(
        self,
        cat_file: Path,
        order_statuses_file: Path,
        cat_prop_type_file: Path,
        cat_prop_val_file: Path,
        cat_prop_file: Path,
        cat_var_type_file: Path,
        cat_var_val_file: Path,
        cat_var_file: Path,
    ) -> None:
        self.categories: List[Category] = self.load_from_file(cat_file, Category)
        self.order_statuses: List[OrderStatus] = self.load_from_file(
            order_statuses_file, OrderStatus
        )
        self.cat_prop_type: List[CategoryPropertyType] = self.load_from_file(
            cat_prop_type_file, CategoryPropertyType
        )

        self.cat_prop_val: List[CategoryPropertyValue] = self.load_from_file(
            cat_prop_val_file, CategoryPropertyValue
        )
        self.cat_prop: List[CategoryProperty] = self.load_from_file(
            cat_prop_file, CategoryProperty
        )
        self.cat_var_type: List[CategoryVariationType] = self.load_from_file(
            cat_var_type_file, CategoryVariationType
        )

        self.cat_var_val: List[CategoryVariationValue] = self.load_from_file(
            cat_var_val_file, CategoryVariationValue
        )
        self.cat_var: List[CategoryVariation] = self.load_from_file(
            cat_var_file, CategoryVariation
        )

    def load_from_file(self, filepath: Path, model: CRUD) -> List[Any]:
        with open(filepath, encoding="utf-8") as f:
            elements = csv.DictReader(f)
            modeled_elements = []
            for el in elements:
                if el.get("uuid", None):
                    el["uuid"] = UUID(el["uuid"], version=4)
                for k in el.keys():
                    if el[k] == "":
                        el[k] = None
                modeled_elements.append(model(**el))
            return modeled_elements

    async def load_to_db(self, table: Type[CRUD], entities_to_load: list[ORMSchema]) -> None:
        success_count = 0
        async with async_sessionmaker.begin() as session:
            for entity in entities_to_load:
                try:
                    await table.insert_one(  # type: ignore
                        session=session, values={**entity.dict()}
                    )
                    success_count += 1
                except Exception as ex:
                    logger.warning(f"{table} {entity.id} {ex}")
        logger.info(
            f"loaded {success_count} rows to {table.__model__.__tablename__}"  # type: ignore
        )

    async def load_constants(self) -> None:
        await self.load_to_db(crud.categories, self.categories)
        await self.load_to_db(crud.orders_statuses, self.order_statuses)
        await self.load_to_db(crud.categories_property_types, self.cat_prop_type)
        await self.load_to_db(crud.categories_property_values, self.cat_prop_val)
        await self.load_to_db(crud.categories_properties, self.cat_prop)
        await self.load_to_db(crud.categories_variation_types, self.cat_var_type)
        await self.load_to_db(crud.categories_variation_values, self.cat_var_val)
        await self.load_to_db(crud.categories_variations, self.cat_var)


loader = LoadFromFile(
    cat_file=CATEGORIES_FILE,
    order_statuses_file=ORDER_STATUSES_FILE,
    cat_prop_type_file=CAT_PROP_TYPE_FILE,
    cat_prop_val_file=CAT_PROP_VAL_FILE,
    cat_prop_file=CAT_PROP_FILE,
    cat_var_type_file=CAT_VAR_TYPE_FILE,
    cat_var_val_file=CAT_VAR_VAL_FILE,
    cat_var_file=CAT_VAR_FILE,
)
