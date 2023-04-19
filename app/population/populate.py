# mypy: ignore-errors

import asyncio
import csv
import random
from pathlib import Path
from typing import Any, List
from uuid import UUID

from faker import Faker
from faker.providers.phone_number import Provider as PhoneNumberProvider
from loguru import logger
from sqlalchemy.exc import IntegrityError

from core.orm import orm
from orm import SellerModel, SupplierModel
from orm.core.session import async_sessionmaker
from schemas import (
    Category,
    Company,
    Product,
    User,
    OrderStatus,
    Order,
    CategoryVariation,
    CategoryPropertyType,
    CategoryPropertyValue,
    CategoryProperty,
    CategoryVariationType,
    CategoryVariationValue,
    ProductVariationValue,
    OrderProductVariation,
)
from schemas.orm.core import ORMSchema


class OurPhoneNumberProvider(PhoneNumberProvider):
    def our_phone_number(self) -> Any:
        return self.msisdn()[3:]


faker: Faker = Faker()
faker.add_provider(OurPhoneNumberProvider)


DATA_DIR = Path("app/population/data")
USER_FILE = DATA_DIR / "users.csv"
SELLERS_FILE = DATA_DIR / "sellers.csv"
PRODUCTS_FILE = DATA_DIR / "products.csv"
CATEGORIES_FILE = DATA_DIR / "categories.csv"
ORDER_STATUSES_FILE = DATA_DIR / "order_stasuses.csv"
ORDERS_FILE = DATA_DIR / "orders.csv"
CAT_PROP_TYPE_FILE = DATA_DIR / "category_property_type.csv"
CAT_PROP_VAL_FILE = DATA_DIR / "category_property_value.csv"
CAT_PROP_FILE = DATA_DIR / "category_properties.csv"
CAT_VAR_TYPE_FILE = DATA_DIR / "category_variation_type.csv"
CAT_VAR_VAL_FILE = DATA_DIR / "category_variation_value.csv"
PROD_VAR_VAL_FILE = DATA_DIR / "product_variation_value.csv"
CAT_VAR_FILE = DATA_DIR / "category_variation.csv"
COMPANY_FILE = DATA_DIR / "company.csv"
ORDERS_FILE = DATA_DIR / "order.csv"
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
    def __init__(
        self,
        users_file: Path,
        products_file: Path,
        cat_file: Path,
        order_statuses_file: Path,
        orders_file: Path,
        cat_prop_type_file: Path,
        cat_prop_val_file: Path,
        cat_prop_file: Path,
        cat_var_type_file: Path,
        cat_var_val_file: Path,
        prod_var_val_file: Path,
        cat_var_file: Path,
        company_file: Path,
        order_file: Path,
        order_prod_var_file: Path,
    ) -> None:
        self.users: List[User] = self.load_from_file(users_file, User)
        self.products: List[Product] = self.load_from_file(products_file, UploadProduct)
        self.categories: List[Category] = self.load_from_file(cat_file, Category)
        self.order_statuses: List[OrderStatus] = self.load_from_file(
            order_statuses_file, OrderStatus
        )
        # self.orders: List[Order] = self.load_from_file()
        self.cat_prop_type: List[CategoryPropertyType] = self.load_from_file(
            cat_prop_type_file, CategoryPropertyType
        )

        self.prod_var_val: List[ProductVariationValue] = self.load_from_file(
            prod_var_val_file, ProductVariationValue
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
        self.companies: List[UploadCompany] = self.load_from_file(company_file, UploadCompany)
        self.orders: List[Order] = self.load_from_file(order_file, Order)

        self.order_prod_var: List[UploadOrderProductVariation] = self.load_from_file(
            order_prod_var_file, UploadOrderProductVariation
        )

    def load_from_file(self, filepath: Path, model: ORMSchema) -> List[Any]:
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

    async def load_to_db(self, table: Any, entities_to_load: list) -> None:
        success_count = 0
        for entity in entities_to_load:
            try:
                async with async_sessionmaker.begin() as session:
                    await table.insert_one(  # type: ignore
                        session=session, values={**entity.dict()}
                    )
                    success_count += 1
            except IntegrityError as ex:
                logger.warning(f"{table} {entity.id} {ex}")
        logger.info(
            f"loaded {success_count} rows to {table.__model__.__tablename__}"  # type: ignore
        )

    async def load_suppliers_and_sellers(self) -> None:
        for user in self.users:
            try:
                async with async_sessionmaker.begin() as session:
                    if user.is_supplier:
                        await orm.suppliers.insert_one(
                            session=session,
                            values={
                                SupplierModel.user_id: user.id,
                                SupplierModel.grade_average: random.uniform(0.0, 5.0),
                                SupplierModel.license_number: "".join(
                                    [str(random.randint(1, 10)) for _ in range(1, 10)]
                                ),
                                SupplierModel.additional_info: faker.paragraph(
                                    nb_sentences=random.randrange(5, 11)
                                ),
                            },
                        )
                    else:
                        await orm.sellers.insert_one(
                            session=session,
                            values={SellerModel.user_id: user.id},
                        )
                    logger.debug(f"user_id {user.id} -- OK")
            except IntegrityError as ex:
                logger.debug(f"user_id {user.id}")
                logger.warning(ex)

    async def load_stock(self):
        product_variation_value1_id = 1
        product_variation_value2_id = 2
        for _ in range(198):
            try:
                async with async_sessionmaker.begin() as session:
                    await orm.products_variation_counts.insert_one(
                        session=session,
                        values={
                            "count": random.randint(0, 100),
                            "product_variation_value1_id": product_variation_value1_id,
                            "product_variation_value2_id": product_variation_value2_id,
                        },
                    )
                    product_variation_value1_id += 2
                    product_variation_value2_id += 2
            except Exception as ex:
                logger.warning(ex)

    def main_load(self) -> None:
        loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.load_to_db(orm.users, self.users))
        # loop.run_until_complete(self.load_suppliers_and_sellers())
        # loop.run_until_complete(self.load_to_db(orm.categories, self.categories))
        # loop.run_until_complete(self.load_to_db(orm.products, self.products))
        # loop.run_until_complete(self.load_to_db(orm.orders_statuses, self.order_statuses))
        # # loop.run_until_complete(self.load_to_db(orm.orders, self.orders))
        # loop.run_until_complete(self.load_to_db(orm.categories_property_types, self.cat_prop_type))
        # loop.run_until_complete(self.load_to_db(orm.categories_property_values, self.cat_prop_val))
        # loop.run_until_complete(self.load_to_db(orm.categories_properties, self.cat_prop))
        # loop.run_until_complete(self.load_to_db(orm.categories_variation_types, self.cat_var_type))
        # loop.run_until_complete(self.load_to_db(orm.categories_variation_values, self.cat_var_val))
        # loop.run_until_complete(self.load_to_db(orm.categories_variations, self.cat_var))
        # loop.run_until_complete(self.load_to_db(orm.companies, self.companies))
        # loop.run_until_complete(self.load_to_db(orm.products_variation_values, self.prod_var_val))
        # FIXME: redo
        # loop.run_until_complete(self.load_stock())
        # loop.run_until_complete(self.load_to_db(orm.orders, self.orders))
        loop.run_until_complete(
            self.load_to_db(orm.orders_products_variation, self.order_prod_var)
        )


uploader = LoadFromFile(
    users_file=USER_FILE,
    products_file=PRODUCTS_FILE,
    cat_file=CATEGORIES_FILE,
    order_statuses_file=ORDER_STATUSES_FILE,
    orders_file=ORDERS_FILE,
    cat_prop_type_file=CAT_PROP_TYPE_FILE,
    cat_prop_val_file=CAT_PROP_VAL_FILE,
    cat_prop_file=CAT_PROP_FILE,
    cat_var_type_file=CAT_VAR_TYPE_FILE,
    cat_var_val_file=CAT_VAR_VAL_FILE,
    prod_var_val_file=PROD_VAR_VAL_FILE,
    cat_var_file=CAT_VAR_FILE,
    company_file=COMPANY_FILE,
    order_file=ORDERS_FILE,
    order_prod_var_file=ORDER_PRODUCT_VAR_FILE,
)
