from __future__ import annotations

import abc
from dataclasses import dataclass, fields
from datetime import datetime, timedelta
from random import choice, randint, randrange, uniform
from typing import List, Type, TypeVar

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from core.app import crud
from core.security import hash_password
from orm import (
    CategoryModel,
    CategoryPropertyValueModel,
    CompanyModel,
    OrderModel,
    OrderProductVariationModel,
    OrderStatusModel,
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
from orm.core import ORMModel, async_sessionmaker

from .settings import admin_settings

T = TypeVar("T", bound=ORMModel)


async def entities(session: AsyncSession, orm_model: Type[T]) -> List[int]:
    return [
        entity.id
        for entity in await crud.raws.get_many(
            orm_model.id,
            session=session,
            select_from=[orm_model],
        )
    ]


class BaseGenerator(abc.ABC):
    faker: Faker = Faker()

    @abc.abstractmethod
    async def _load(self, session: AsyncSession) -> None:
        ...

    async def load(self, size: int = 100) -> None:
        async def load(_obj: BaseGenerator, session: AsyncSession, _size: int) -> None:
            for _ in range(size):
                await _obj._load(session=session)

        async with async_sessionmaker.begin() as _session:
            await load(_obj=self, session=_session, _size=size)


class ProductsPricesGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        categories, suppliers = (
            await entities(session=session, orm_model=CategoryModel),
            await entities(session=session, orm_model=SupplierModel),
        )

        product = await crud.products.insert_one(
            session=session,
            values={
                ProductModel.name: self.faker.sentence(nb_words=randint(1, 4)),
                ProductModel.description: self.faker.sentence(nb_words=10),
                ProductModel.category_id: choice(categories),
                ProductModel.datetime: datetime.now(),
                ProductModel.supplier_id: choice(suppliers),
                ProductModel.grade_average: uniform(0.0, 5.0),
                ProductModel.is_active: True,
            },
        )

        await crud.products_prices.insert_one(
            session=session,
            values={
                ProductPriceModel.product_id: product.id,
                ProductPriceModel.value: uniform(100.0, 10000.0),
                ProductPriceModel.start_date: datetime.now(),
                ProductPriceModel.end_date: datetime.now() + timedelta(days=randint(1, 1000)),
                ProductPriceModel.discount: uniform(0.0, 0.9),
                ProductPriceModel.min_quantity: randint(1, 100),
            },
        )


class UsersGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        supplier = choice([True, False])

        user = await crud.users.insert_one(
            session=session,
            values={
                UserModel.is_supplier: supplier,
                UserModel.email: self.faker.email(),
                UserModel.is_verified: True,
                UserModel.first_name: self.faker.first_name(),
                UserModel.last_name: self.faker.last_name(),
                UserModel.phone_number: self.faker.msisdn(),
            },
        )
        await crud.users_credentials.insert_one(
            session=session,
            values={
                UserCredentialsModel.user_id: user.id,
                UserCredentialsModel.password: hash_password(admin_settings.ADMIN_PASSWORD),
            },
        )
        if user.is_supplier:
            await crud.suppliers.insert_one(
                session=session,
                values={
                    SupplierModel.user_id: user.id,
                    SupplierModel.grade_average: uniform(0.0, 5.0),
                    SupplierModel.license_number: self.faker.msisdn(),
                    SupplierModel.additional_info: self.faker.paragraph(
                        nb_sentences=randrange(5, 11),
                    ),
                },
            )
        else:
            await crud.sellers.insert_one(
                session=session,
                values={SellerModel.user_id: user.id},
            )


class OrderGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        order_statuses, sellers = (
            await entities(session=session, orm_model=OrderStatusModel),
            await entities(session=session, orm_model=SellerModel),
        )

        await crud.orders.insert_one(
            session=session,
            values={
                OrderModel.datetime: datetime.now(),
                OrderModel.is_cart: choice([True, False]),
                OrderModel.seller_id: choice(sellers),
                OrderModel.status_id: choice(order_statuses),
            },
        )


class ProductPropertyValueGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        properties = await entities(session=session, orm_model=CategoryPropertyValueModel)

        for product in await entities(session=session, orm_model=ProductModel):
            await crud.products_property_values.insert_one(
                session=session,
                values={
                    ProductPropertyValueModel.product_id: product,
                    ProductPropertyValueModel.property_value_id: choice(properties),
                },
            )

    async def load(self, size: int = 100) -> None:
        await super(ProductPropertyValueGenerator, self).load(size=1)


class StockGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        colors, sizes = await crud.categories_variation_values.get_many_by(
            session=session,
            variation_type_id=1,
        ), await crud.categories_variation_values.get_many_by(
            session=session,
            variation_type_id=2,
        )

        products = await entities(session=session, orm_model=ProductModel)

        color, size, product = choice(colors), choice(sizes), choice(products)

        (
            product_variation_color,
            product_variation_size,
        ) = await crud.products_variation_values.insert_many(  # noqa
            session=session,
            values=[
                {
                    ProductVariationValueModel.product_id: product,
                    ProductVariationValueModel.variation_value_id: color.id,
                },
                {
                    ProductVariationValueModel.product_id: product,
                    ProductVariationValueModel.variation_value_id: size.id,
                },
            ],
        )

        await crud.products_variation_counts.insert_one(
            session=session,
            values={
                ProductVariationCountModel.count: randint(0, 100),
                ProductVariationCountModel.product_variation_value1_id: product_variation_color.id,
                ProductVariationCountModel.product_variation_value2_id: product_variation_size.id,
            },
        )


class CompanyGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        suppliers = await entities(session=session, orm_model=SupplierModel)

        await crud.companies.insert_one(
            session=session,
            values={
                CompanyModel.name: self.faker.company(),
                CompanyModel.description: self.faker.paragraph(nb_sentences=10),
                CompanyModel.business_email: self.faker.email(),
                CompanyModel.supplier_id: choice(suppliers),
                CompanyModel.is_manufacturer: choice([True, False]),
                CompanyModel.number_of_employees: randint(1, 1000),
                CompanyModel.year_established: randint(1950, 2022),
                CompanyModel.address: self.faker.address(),
                CompanyModel.logo_url: self.faker.image_url(),
                CompanyModel.business_sector: self.faker.paragraph(nb_sentences=1)[:30],
            },
        )


class OrderProductVariationGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        order_statuses, orders, product_variation_counts = (
            await entities(session=session, orm_model=OrderStatusModel),
            await entities(session=session, orm_model=OrderModel),
            await entities(session=session, orm_model=ProductVariationCountModel),
        )

        await crud.orders_products_variation.insert_one(
            session=session,
            values={
                OrderProductVariationModel.order_id: choice(orders),
                OrderProductVariationModel.status_id: choice(order_statuses),
                OrderProductVariationModel.product_variation_count_id: choice(
                    product_variation_counts
                ),
                OrderProductVariationModel.count: randint(1, 10),
            },
        )


@dataclass(
    repr=False,
    eq=True,
    frozen=True,
    order=True,
)
class Generator:
    users_generator: UsersGenerator = UsersGenerator()
    product_price_generator: ProductsPricesGenerator = ProductsPricesGenerator()
    order_generator: OrderGenerator = OrderGenerator()
    company_generator: CompanyGenerator = CompanyGenerator()
    stock_generator: StockGenerator = StockGenerator()
    order_product_variation_generator: OrderProductVariationGenerator = (
        OrderProductVariationGenerator()
    )
    product_property_value_generator: ProductPropertyValueGenerator = (
        ProductPropertyValueGenerator()
    )

    async def setup(self) -> None:
        for field in fields(self):
            await getattr(Generator, field.name).load()


generator = Generator()
