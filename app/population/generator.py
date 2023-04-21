# mypy: ignore-errors
import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Type

from faker import Faker
from loguru import logger
from sqlalchemy.exc import IntegrityError

from core.app import crud

from core.app.crud import _CRUD
from core.security import hash_password
from orm import (
    CategoryVariationValueModel,
    CompanyModel,
    OrderModel,
    OrderProductVariationModel,
    ProductModel,
    ProductPriceModel,
    ProductPropertyValueModel,
    ProductVariationCountModel,
    ProductVariationValueModel,
    SellerModel,
    SupplierModel,
    UserCredentialsModel,
    UserModel,
)
from orm.core.session import async_sessionmaker
from schemas import Product

faker: Faker = Faker()

ADMIN_PASSWORD = "Password1!"


class DataGen:
    """Generates and loads random data."""

    def __init__(self) -> None:
        self.loop = asyncio.get_event_loop()

    def load_constants(self):
        self.cat_ids = self.loop.run_until_complete(
            self.get_existing_ids(crud.categories)
        )
        self.order_status_ids = self.loop.run_until_complete(
            self.get_existing_ids(crud.orders_statuses)
        )

    async def get_existing_ids(self, model: Type[_CRUD]) -> list[int]:
        async with async_sessionmaker.begin() as session:
            return [el.id for el in await model.get_many(session=session)]

    async def _load_products_with_prices(self, how_many: int = 100) -> list[Product]:
        suppliers_ids = await self.get_existing_ids(crud.suppliers)
        if not suppliers_ids:
            raise ValueError("not suppliers found")
        for _ in range(how_many):
            async with async_sessionmaker.begin() as session:
                product: ProductModel = await crud.products.insert_one(
                    session=session,
                    values={
                        ProductModel.name: faker.sentence(
                            nb_words=random.randint(1, 4)
                        ),
                        ProductModel.description: faker.sentence(nb_words=10),
                        ProductModel.category_id: random.choice(self.cat_ids),
                        ProductModel.datetime: datetime.now(),
                        ProductModel.supplier_id: random.choice(suppliers_ids),
                        ProductModel.grade_average: random.uniform(0.0, 5.0),
                        ProductModel.is_active: True,
                    },
                )

                await crud.products_prices.insert_one(
                    session=session,
                    values={
                        ProductPriceModel.product_id: product.id,
                        ProductPriceModel.value: random.uniform(100.0, 10000.0),
                        ProductPriceModel.start_date: datetime.now(),
                        ProductPriceModel.end_date: datetime.now()
                        + timedelta(days=random.randint(1, 1000)),
                        ProductPriceModel.discount: random.uniform(0.0, 0.9),
                        ProductPriceModel.min_quantity: random.randint(1, 100),
                    },
                )

                logger.info(f"добавили {product}")

    async def _load_orders(self, how_many: int = 100):
        sellers_ids = await self.get_existing_ids(crud.sellers)
        if not sellers_ids:
            raise ValueError("not suppliers found")
        for _ in range(how_many):
            async with async_sessionmaker.begin() as session:
                order = await crud.orders.insert_one(
                    session=session,
                    values={
                        OrderModel.datetime: datetime.now(),
                        OrderModel.is_cart: random.choice([True, False]),
                        OrderModel.seller_id: random.choice(sellers_ids),
                        OrderModel.status_id: random.choice(self.order_status_ids),
                    },
                )
                logger.info(f"загрузили {order}")

    async def _load_admin_users(self):
        try:
            async with async_sessionmaker.begin() as session:
                seller = await crud.users.insert_one(
                    session=session,
                    values={
                        UserModel.is_supplier: False,
                        UserModel.email: "seller@mail.ru",
                        UserModel.is_verified: True,
                        UserModel.first_name: faker.first_name(),
                        UserModel.last_name: faker.last_name(),
                        UserModel.phone_number: faker.msisdn(),
                    },
                )
                await crud.users_credentials.insert_one(
                    session=session,
                    values={
                        UserCredentialsModel.user_id: seller.id,
                        UserCredentialsModel.password: hash_password(ADMIN_PASSWORD),
                    },
                )

                supplier = await crud.users.insert_one(
                    session=session,
                    values={
                        UserModel.is_supplier: True,
                        UserModel.email: "supplier@mail.ru",
                        UserModel.is_verified: True,
                        UserModel.first_name: faker.first_name(),
                        UserModel.last_name: faker.last_name(),
                        UserModel.phone_number: faker.msisdn(),
                    },
                )
                await crud.users_credentials.insert_one(
                    session=session,
                    values={
                        UserCredentialsModel.user_id: supplier.id,
                        UserCredentialsModel.password: hash_password(ADMIN_PASSWORD),
                    },
                )
        except IntegrityError:
            pass

    async def _load_sellers_and_suppliers(self, how_many: int = 10):
        for i in range(how_many):
            supplier = i % 2 == 0
            async with async_sessionmaker.begin() as session:
                user = await crud.users.insert_one(
                    session=session,
                    values={
                        UserModel.is_supplier: supplier,
                        UserModel.email: faker.email(),
                        UserModel.is_verified: True,
                        UserModel.first_name: faker.first_name(),
                        UserModel.last_name: faker.last_name(),
                        UserModel.phone_number: faker.msisdn(),
                    },
                )
                await crud.users_credentials.insert_one(
                    session=session,
                    values={
                        UserCredentialsModel.user_id: user.id,
                        UserCredentialsModel.password: hash_password(ADMIN_PASSWORD),
                    },
                )
                if user.is_supplier:
                    await crud.suppliers.insert_one(
                        session=session,
                        values={
                            SupplierModel.user_id: user.id,
                            SupplierModel.grade_average: random.uniform(0.0, 5.0),
                            SupplierModel.license_number: "".join(
                                [str(random.randint(1, 10)) for _ in range(1, 10)]
                            ),
                            SupplierModel.additional_info: faker.paragraph(
                                nb_sentences=random.randrange(5, 11),
                            ),
                        },
                    )
                else:
                    await crud.sellers.insert_one(
                        session=session,
                        values={SellerModel.user_id: user.id},
                    )

    async def _load_properties_for_product(self):
        async with async_sessionmaker.begin() as session:
            properties_ids = await self.get_existing_ids(
                crud.categories_property_values
            )
            products_ids = await self.get_existing_ids(crud.products)
            for p_id in products_ids:
                await crud.products_property_values.insert_one(
                    session=session,
                    values={
                        ProductPropertyValueModel.product_id: p_id,
                        ProductPropertyValueModel.property_value_id: random.choice(
                            properties_ids
                        ),
                    },
                )
            logger.info(f"loaded {len(products_ids)} prperties for products")

    async def _load_stock(self, how_many: int = 100):
        """Loads products with a set of vars (color&size) and their quantity."""

        async with async_sessionmaker.begin() as session:
            # two category types (size and color so far)
            cat_var_type_1 = await crud.categories_variation_values.get_many(
                session=session,
                where=[CategoryVariationValueModel.variation_type_id == 1],
            )
            cat_var_type_2 = await crud.categories_variation_values.get_many(
                session=session,
                where=[CategoryVariationValueModel.variation_type_id == 2],
            )
            if not cat_var_type_1 and cat_var_type_2:
                raise ValueError("categories variations not found in db")

            cat_var_type_1_ids = [el.id for el in cat_var_type_1]
            cat_var_type_2_ids = [el.id for el in cat_var_type_2]

            product_ids = await self.get_existing_ids(crud.products)

        async with async_sessionmaker.begin() as session:
            for _ in range(how_many):
                var_val_1 = random.choice(cat_var_type_1_ids)
                var_val_2 = random.choice(cat_var_type_2_ids)
                prod_id = random.choice(product_ids)

                # inserting products with a set of vars (color&size)
                product_var_vals: List[
                    ProductVariationValueModel
                ] = await crud.products_variation_values.insert_many(
                    session=session,
                    values=[
                        {
                            ProductVariationValueModel.product_id: prod_id,
                            ProductVariationValueModel.variation_value_id: var_val_1,
                        },
                        {
                            ProductVariationValueModel.product_id: prod_id,
                            ProductVariationValueModel.variation_value_id: var_val_2,
                        },
                    ],
                )
                # inserting product stock quantity
                await crud.products_variation_counts.insert_one(
                    session=session,
                    values={
                        ProductVariationCountModel.count: random.randint(0, 100),
                        ProductVariationCountModel.product_variation_value1_id: product_var_vals[
                            0
                        ].id,
                        ProductVariationCountModel.product_variation_value2_id: product_var_vals[
                            1
                        ].id,
                    },
                )
            logger.info(f"loaded {how_many} ")

    async def _load_companies(self, how_many: int = 30):
        suppliers_ids = await self.get_existing_ids(crud.suppliers)
        if not suppliers_ids:
            raise ValueError("no suppliers found in db")

        async with async_sessionmaker.begin() as session:
            for _ in range(how_many):
                await crud.companies.insert_one(
                    session=session,
                    values={
                        CompanyModel.name: faker.company(),
                        CompanyModel.description: faker.paragraph(
                            nb_sentences=10,
                        ),
                        CompanyModel.business_email: faker.email(),
                        CompanyModel.supplier_id: random.choice(suppliers_ids),
                        CompanyModel.is_manufacturer: random.choice([True, False]),
                        CompanyModel.number_of_employees: random.randint(1, 1000),
                        CompanyModel.year_established: random.randint(1950, 2022),
                        CompanyModel.address: faker.address(),
                        CompanyModel.logo_url: faker.image_url(),
                        CompanyModel.business_sector: faker.paragraph(
                            nb_sentences=1,
                        )[:25],
                    },
                )
        logger.info(f"loaded {how_many} companies")

    async def _load_orders(self, how_many: int = 100):
        sellers_ids = await self.get_existing_ids(crud.sellers)
        if not sellers_ids:
            raise ValueError("not suppliers found")

        async with async_sessionmaker.begin() as session:
            for _ in range(how_many):
                await crud.orders.insert_one(
                    session=session,
                    values={
                        OrderModel.seller_id: random.choice(sellers_ids),
                        OrderModel.is_cart: random.choice([True, False]),
                        OrderModel.status_id: random.choice(self.order_status_ids),
                    },
                )
        logger.info(f"loaded {how_many} orders")

    async def _load_order_product_variation(self, how_many: int = 100):
        async with async_sessionmaker.begin() as session:
            prod_var_count_ids = await self.get_existing_ids(
                crud.products_variation_counts
            )
            order_ids = await self.get_existing_ids(crud.orders)
            if not prod_var_count_ids:
                raise ValueError("no prod_var_count_ids laoded")
            if not order_ids:
                raise ValueError("no orders loaded")

            for _ in range(how_many):
                await crud.orders_products_variation.insert_one(
                    session=session,
                    values={
                        OrderProductVariationModel.order_id: random.choice(order_ids),
                        OrderProductVariationModel.status_id: random.choice(
                            self.order_status_ids
                        ),
                        OrderProductVariationModel.product_variation_count_id: random.choice(
                            prod_var_count_ids
                        ),
                        OrderProductVariationModel.count: random.randint(1, 10),
                    },
                )
            logger.info(f"loaded {how_many} order_product_variation")

    def load_products(self):
        self.loop.run_until_complete(self._load_products_with_prices())

    def load_sellers_and_suppliers(self):
        self.loop.run_until_complete(self._load_sellers_and_suppliers())

    def load_admin_users(self):
        self.loop.run_until_complete(self._load_admin_users())

    def load_stock(self):
        self.loop.run_until_complete(self._load_stock())

    def load_companies(self):
        self.loop.run_until_complete(self._load_companies())

    def load_orders(self):
        self.loop.run_until_complete(self._load_orders())

    def load_order_product_var(self):
        self.loop.run_until_complete(self._load_order_product_variation())

    def load_properties_for_product(self):
        self.loop.run_until_complete(self._load_properties_for_product())

    def load_all(self):
        self.load_constants()
        self.load_sellers_and_suppliers()
        self.load_admin_users()
        self.load_products()
        self.load_orders()
        self.load_companies()
        self.load_stock()
        self.load_order_product_var()
        self.load_properties_for_product()


data_generator = DataGen()
