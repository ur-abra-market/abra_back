""" populate.py
    Best module ever

   isort:skip_file
"""
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
from schemas import Category, ORMSchema, Product, User


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


class TablesMapper:
    categories = orm.categories
    users = orm.users
    products = orm.products


class LoadingProduct(Product):
    category_id: int
    supplier_id: int


class LoadFromFile:
    def __init__(self, users_file: Path, products_file: Path, cat_file: Path) -> None:
        self.users: List[User] = self.load_from_file(users_file, User)
        self.products: List[Product] = self.load_from_file(products_file, LoadingProduct)
        self.categories: List[Category] = self.load_from_file(cat_file, Category)

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

    async def load_to_db(self, table: TablesMapper) -> None:
        entities_to_load = []
        if table == TablesMapper.users:
            entities_to_load = self.users
        elif table == TablesMapper.categories:
            entities_to_load = self.categories
        elif table == TablesMapper.products:
            entities_to_load = self.products

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

    def main_load(self) -> None:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.load_to_db(TablesMapper.users))
        loop.run_until_complete(self.load_suppliers_and_sellers())
        loop.run_until_complete(self.load_to_db(TablesMapper.categories))
        loop.run_until_complete(self.load_to_db(TablesMapper.products))


uploader = LoadFromFile(
    users_file=USER_FILE, products_file=PRODUCTS_FILE, cat_file=CATEGORIES_FILE
)
