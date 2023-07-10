from __future__ import annotations

import abc
from dataclasses import dataclass, fields
from datetime import datetime, timedelta
from random import choice, randint, randrange, uniform
from typing import Any, List, Type, TypeVar

from corecrud import Options, Returning, SelectFrom, Values, Where
from faker import Faker
from phone_gen import PhoneNumber
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from core.app import crud
from core.security import hash_password
from orm import (
    CategoryModel,
    CategoryPropertyValueModel,
    CategoryVariationValueModel,
    CompanyModel,
    CompanyPhoneModel,
    CountryModel,
    OrderModel,
    OrderProductVariationModel,
    OrderStatusModel,
    ProductImageModel,
    ProductModel,
    ProductPriceModel,
    ProductPropertyValueModel,
    ProductVariationCountModel,
    ProductVariationValueModel,
    SellerImageModel,
    SellerModel,
    SellerNotificationsModel,
    SupplierModel,
    SupplierNotificationsModel,
    UserCredentialsModel,
    UserModel,
)
from orm.core import ORMModel, async_sessionmaker

from .settings import admin_settings, user_settings

T = TypeVar("T", bound=ORMModel)


async def entities(session: AsyncSession, orm_model: Type[T]) -> List[Any]:
    return await crud.raws.select.many(
        SelectFrom(orm_model),
        nested_select=[orm_model.id],
        session=session,
    )


async def category_entities(session: AsyncSession, orm_model: Type[T]) -> List[Any]:
    return await crud.raws.select.many(
        SelectFrom(orm_model),
        Where(orm_model.level == 3),
        nested_select=[orm_model.id],
        session=session,
    )


async def country_entities(session: AsyncSession, orm_model: Type[T]) -> List[Any]:
    return await crud.raws.select.many(
        SelectFrom(orm_model),
        nested_select=[orm_model.id, orm_model.country],
        session=session,
    )


def get_image_url(width: int, height: int) -> str:
    urls = [
        "https://placekitten.com/{width}/{height}?image={image}".format(
            width=width, height=height, image=randint(1, 16)
        ),
        "https://picsum.photos/id/{image}/{width}/{height}".format(
            width=width, height=height, image=randint(1, 500)
        ),
    ]
    return choice(urls)


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
        categories = await category_entities(session=session, orm_model=CategoryModel)
        suppliers = await entities(session=session, orm_model=SupplierModel)
        for category in categories:
            product = await crud.products.insert.one(
                Values(
                    {
                        ProductModel.name: self.faker.sentence(nb_words=randint(1, 4)),
                        ProductModel.description: self.faker.sentence(nb_words=10),
                        ProductModel.category_id: category.id,
                        ProductModel.datetime: datetime.now(),
                        ProductModel.supplier_id: choice(suppliers).id,
                        ProductModel.grade_average: uniform(0.0, 5.0),
                        ProductModel.is_active: True,
                    },
                ),
                Returning(ProductModel),
                session=session,
            )

            await crud.products_prices.insert.one(
                Values(
                    {
                        ProductPriceModel.product_id: product.id,
                        ProductPriceModel.value: uniform(100.0, 10000.0),
                        ProductPriceModel.start_date: datetime.now(),
                        ProductPriceModel.end_date: datetime.now()
                        + timedelta(days=randint(1, 1000)),
                        ProductPriceModel.discount: uniform(0.0, 0.9),
                        ProductPriceModel.min_quantity: randint(1, 100),
                    }
                ),
                Returning(ProductPriceModel.id),
                session=session,
            )

            await crud.products_images.insert.many(
                Values(
                    [
                        {
                            ProductImageModel.product_id: product.id,
                            ProductImageModel.image_url: self.faker.image_url(
                                placeholder_url=get_image_url(width=220, height=220)
                            ),
                        }
                        for _ in range(randint(1, 10))
                    ]
                ),
                Returning(ProductImageModel.id),
                session=session,
            )

    async def load(self, size: int = randint(0, 50)) -> None:
        await super(ProductsPricesGenerator, self).load(size=randint(0, 50))


class UsersGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        countries = await entities(session=session, orm_model=CountryModel)

        user = await crud.users.insert.one(
            Values(
                {
                    UserModel.is_supplier: choice([True, False]),
                    UserModel.is_deleted: False,
                    UserModel.email: f"{randint(1, 1_000_000)}{self.faker.email()}",
                    UserModel.is_verified: True,
                    UserModel.first_name: self.faker.first_name(),
                    UserModel.last_name: self.faker.last_name(),
                    UserModel.phone_number: self.faker.msisdn(),
                    UserModel.country_id: choice(countries).id,
                }
            ),
            Returning(UserModel),
            session=session,
        )
        await crud.users_credentials.insert.one(
            Values(
                {
                    UserCredentialsModel.user_id: user.id,
                    UserCredentialsModel.password: hash_password(admin_settings.ADMIN_PASSWORD),
                }
            ),
            Returning(UserCredentialsModel.id),
            session=session,
        )
        if user.is_supplier:
            supplier = await crud.suppliers.insert.one(
                Values(
                    {
                        SupplierModel.user_id: user.id,
                        SupplierModel.grade_average: uniform(0.0, 5.0),
                        SupplierModel.license_number: self.faker.msisdn(),
                        SupplierModel.additional_info: self.faker.paragraph(
                            nb_sentences=randrange(5, 11),
                        ),
                    }
                ),
                Returning(SupplierModel),
                session=session,
            )
            await crud.suppliers_notifications.insert.one(
                Values({SupplierNotificationsModel.supplier_id: supplier.id}),
                Returning(SupplierNotificationsModel.id),
                session=session,
            )
        else:
            seller = await crud.sellers.insert.one(
                Values({SellerModel.user_id: user.id}),
                Returning(SellerModel),
                session=session,
            )
            await crud.sellers_notifications.insert.one(
                Values({SellerNotificationsModel.seller_id: seller.id}),
                Returning(SellerNotificationsModel.id),
                session=session,
            )


class DefaultUsersGenerator(BaseGenerator):
    counter = 0

    def get_counter(self) -> str:
        return str(self.counter) if self.counter else ""

    async def _load(self, session: AsyncSession) -> None:
        countries = await entities(session=session, orm_model=CountryModel)

        supplier_user = await crud.users.insert.one(
            Values(
                {
                    UserModel.is_deleted: False,
                    UserModel.is_supplier: True,
                    UserModel.email: f"{user_settings.SUPPLIER_EMAIL_LOCAL}{self.get_counter()}@{user_settings.EMAIL_DOMAIN}",
                    UserModel.is_verified: True,
                    UserModel.first_name: "Supplier Name",
                    UserModel.last_name: "Supplier Lastname",
                    UserModel.phone_number: "794903531516",
                    UserModel.country_id: choice(countries).id,
                }
            ),
            Returning(UserModel),
            session=session,
        )

        supplier = await crud.suppliers.insert.one(
            Values(
                {
                    SupplierModel.user_id: supplier_user.id,
                    SupplierModel.grade_average: 0.0,
                    SupplierModel.license_number: "3255900647702",
                    SupplierModel.additional_info: "Supplier additional info",
                }
            ),
            Returning(SupplierModel),
            session=session,
        )

        await crud.suppliers_notifications.insert.one(
            Values({SupplierNotificationsModel.supplier_id: supplier.id}),
            Returning(SupplierNotificationsModel.id),
            session=session,
        )

        await crud.users_credentials.insert.one(
            Values(
                {
                    UserCredentialsModel.user_id: supplier_user.id,
                    UserCredentialsModel.password: hash_password(user_settings.DEFAULT_PASSWORD),
                }
            ),
            Returning(UserCredentialsModel.id),
            session=session,
        )

        seller_user = await crud.users.insert.one(
            Values(
                {
                    UserModel.is_deleted: False,
                    UserModel.email: f"{user_settings.SELLER_EMAIL_LOCAL}{self.get_counter()}@{user_settings.EMAIL_DOMAIN}",
                    UserModel.is_verified: True,
                    UserModel.first_name: "Seller Name",
                    UserModel.last_name: "Seller Lastname",
                    UserModel.phone_number: "3255900647702",
                    UserModel.country_id: choice(countries).id,
                }
            ),
            Returning(UserModel),
            session=session,
        )

        seller = await crud.sellers.insert.one(
            Values({SellerModel.user_id: seller_user.id}),
            Returning(SellerModel),
            session=session,
        )

        await crud.sellers_images.insert.one(
            Values(
                {
                    SellerImageModel.seller_id: seller.id,
                    SellerImageModel.source_url: "https://placekitten.com/200/300",
                    SellerImageModel.thumbnail_url: "https://placekitten.com/200/300",
                }
            ),
            session=session,
        )

        await crud.sellers_notifications.insert.one(
            Values({SellerNotificationsModel.seller_id: seller.id}),
            Returning(SellerNotificationsModel.id),
            session=session,
        )

        await crud.users_credentials.insert.one(
            Values(
                {
                    UserCredentialsModel.user_id: seller_user.id,
                    UserCredentialsModel.password: hash_password(user_settings.DEFAULT_PASSWORD),
                }
            ),
            Returning(UserCredentialsModel.id),
            session=session,
        )

        self.counter += 1

    async def load(self, size: int = 100) -> None:
        await super(DefaultUsersGenerator, self).load(size=31)


class OrderGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        order_statuses, sellers = (
            await entities(session=session, orm_model=OrderStatusModel),
            await entities(session=session, orm_model=SellerModel),
        )

        await crud.orders.insert.one(
            Values(
                {
                    OrderModel.datetime: datetime.now(),
                    OrderModel.is_cart: choice([True, False]),
                    OrderModel.seller_id: choice(sellers).id,
                    OrderModel.status_id: choice(order_statuses).id,
                },
            ),
            Returning(OrderModel.id),
            session=session,
        )


class ProductPropertyValueGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        properties = await entities(session=session, orm_model=CategoryPropertyValueModel)

        for product in await entities(session=session, orm_model=ProductModel):
            await crud.products_property_values.insert.one(
                Values(
                    {
                        ProductPropertyValueModel.product_id: product.id,
                        ProductPropertyValueModel.property_value_id: choice(properties).id,
                    }
                ),
                Returning(ProductPropertyValueModel.id),
                session=session,
            )

    async def load(self, size: int = 100) -> None:
        await super(ProductPropertyValueGenerator, self).load(size=1)


class StockGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        colors, sizes = await crud.categories_variation_values.select.many(
            Where(CategoryVariationValueModel.variation_type_id == 1),
            session=session,
        ), await crud.categories_variation_values.select.many(
            Where(CategoryVariationValueModel.variation_type_id == 2),
            session=session,
        )

        products = await entities(session=session, orm_model=ProductModel)

        color, size, product = choice(colors), choice(sizes), choice(products).id

        (
            product_variation_color,
            product_variation_size,
        ) = await crud.products_variation_values.insert.many(
            Values(
                [
                    {
                        ProductVariationValueModel.product_id: product,
                        ProductVariationValueModel.variation_value_id: color.id,
                    },
                    {
                        ProductVariationValueModel.product_id: product,
                        ProductVariationValueModel.variation_value_id: size.id,
                    },
                ],
            ),
            Returning(ProductVariationValueModel.id),
            session=session,
        )

        await crud.products_variation_counts.insert.one(
            Values(
                {
                    ProductVariationCountModel.count: randint(0, 100),
                    ProductVariationCountModel.product_variation_value1_id: product_variation_color,
                    ProductVariationCountModel.product_variation_value2_id: product_variation_size,
                }
            ),
            Returning(ProductVariationCountModel.id),
            session=session,
        )


class CompanyGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        suppliers = await entities(session=session, orm_model=SupplierModel)
        countries = await country_entities(session=session, orm_model=CountryModel)
        supplier = await crud.suppliers.select.one(
            Where(SupplierModel.id == choice(suppliers).id),
            Options(joinedload(SupplierModel.company)),
            session=session,
        )

        if not supplier.company:
            company_id = await crud.companies.insert.one(
                Values(
                    {
                        CompanyModel.name: self.faker.company(),
                        CompanyModel.country_id: choice(countries).id,
                        CompanyModel.description: self.faker.paragraph(nb_sentences=10),
                        CompanyModel.business_email: f"{randint(1, 1_000_000)}{self.faker.email()}",
                        CompanyModel.supplier_id: supplier.id,
                        CompanyModel.is_manufacturer: choice([True, False]),
                        CompanyModel.number_employees: randint(1, 1000),
                        CompanyModel.year_established: randint(1970, 2022),
                        CompanyModel.address: self.faker.address(),
                        CompanyModel.logo_url: self.faker.image_url(),
                        CompanyModel.business_sector: self.faker.paragraph(nb_sentences=1)[:30],
                    }
                ),
                Returning(CompanyModel.id),
                session=session,
            )

            country = choice(countries)
            await crud.companies_phones.insert.one(
                Values(
                    {
                        CompanyPhoneModel.company_id: company_id,
                        CompanyPhoneModel.country_id: country.id,
                        CompanyPhoneModel.phone_number: PhoneNumber(country.country).get_number(
                            full=False
                        ),
                    }
                ),
                Returning(CompanyPhoneModel.id),
                session=session,
            )


class OrderProductVariationGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        order_statuses, orders, product_variation_counts = (
            await entities(session=session, orm_model=OrderStatusModel),
            await entities(session=session, orm_model=OrderModel),
            await entities(session=session, orm_model=ProductVariationCountModel),
        )

        await crud.orders_products_variation.insert.one(
            Values(
                {
                    OrderProductVariationModel.order_id: choice(orders).id,
                    OrderProductVariationModel.status_id: choice(order_statuses).id,
                    OrderProductVariationModel.product_variation_count_id: choice(
                        product_variation_counts
                    ).id,
                    OrderProductVariationModel.count: randint(1, 10),
                },
            ),
            Returning(OrderProductVariationModel.id),
            session=session,
        )


@dataclass(
    repr=False,
    eq=True,
    frozen=True,
    order=True,
)
class Generator:
    default_users_generator: DefaultUsersGenerator = DefaultUsersGenerator()
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
