from __future__ import annotations

import abc
from dataclasses import dataclass, fields
from datetime import datetime
from random import choice, randint, sample, uniform
from typing import Any, List, Type, TypeVar

from corecrud import Options, Returning, SelectFrom, Values, Where
from faker import Faker
from phone_gen import PhoneNumber
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.app import crud
from core.security import hash_password
from orm import (
    BrandModel,
    BundlableVariationValueModel,
    BundleModel,
    BundlePodPriceModel,
    BundleVariationModel,
    BundleVariationPodModel,
    CategoryModel,
    CompanyModel,
    CompanyPhoneModel,
    CountryModel,
    EmployeesNumberModel,
    ProductImageModel,
    ProductModel,
    ProductTagModel,
    SellerImageModel,
    SellerModel,
    SellerNotificationsModel,
    SupplierModel,
    SupplierNotificationsModel,
    TagModel,
    UserCredentialsModel,
    UserModel,
    VariationValueModel,
    VariationValueToProductModel,
)
from orm.core import ORMModel, async_sessionmaker

from .settings import population_settings

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


def entities_generator(entities: List[Any], count: int = 0):
    yield from sample(entities, count)


# async def product_variation_values(session: AsyncSession, orm_model: Type[T], product_id: int) -> List[Any]:
#   return await crud.raws.select.many(
#         SelectFrom(orm_model),
#         Where(orm_model.product_id == product_id),
#         nested_select=[orm_model.id],
#         session=session,
#     )


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
        brands = await entities(session=session, orm_model=BrandModel)
        category_variations = await entities(session=session, orm_model=VariationValueModel)

        tags = await crud.tags.insert.many(
            Values([{TagModel.name: self.faker.sentence(nb_words=1)} for _ in range(50)]),
            Returning(TagModel),
            session=session,
        )

        for supplier in suppliers:
            for category in categories:
                if supplier.id == 1 and category.id == 3:
                    continue
                product_count = randint(0, population_settings.PRODUCTS_COUNT_RANGE)
                for _ in range(product_count):
                    product = await crud.products.insert.one(
                        Values(
                            {
                                ProductModel.name: self.faker.sentence(nb_words=randint(1, 4)),
                                ProductModel.description: self.faker.sentence(nb_words=10),
                                ProductModel.category_id: category.id,
                                ProductModel.datetime: datetime.now(),
                                ProductModel.supplier_id: supplier.id,
                                ProductModel.grade_average: uniform(0.0, 5.0),
                                ProductModel.is_active: True,
                                ProductModel.brand_id: choice(brands).id,
                            },
                        ),
                        Returning(ProductModel),
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
                                    ProductImageModel.order: i,
                                }
                                for i in range(randint(1, 10))
                            ]
                        ),
                        Returning(ProductImageModel),
                        session=session,
                    )

                    await crud.products_tags.insert.many(
                        Values(
                            [
                                {
                                    ProductTagModel.product_id: product.id,
                                    ProductTagModel.tag_id: choice(tags).id,
                                }
                                for _ in range(randint(1, 10))
                            ]
                        ),
                        Returning(ProductTagModel),
                        session=session,
                    )

                    variation_values_to_products_count = randint(5, 10)
                    category_variations_gen = entities_generator(
                        entities=category_variations,
                        count=variation_values_to_products_count,
                    )
                    await crud.variation_values_to_products.insert.many_unique(
                        Values(
                            [
                                {
                                    VariationValueToProductModel.product_id: product.id,
                                    VariationValueToProductModel.variation_value_id: next(
                                        category_variations_gen
                                    ).id,
                                }
                                for _ in range(variation_values_to_products_count)
                            ]
                        ),
                        Returning(VariationValueToProductModel),
                        session=session,
                    )

                    bundle = await crud.bundles.insert.one(
                        Values(
                            {
                                BundleModel.product_id: product.id,
                                BundleModel.stock: randint(10, 30),
                            }
                        ),
                        Returning(BundleModel),
                        session=session,
                    )

                    product_raw = await crud.products.select.many_unique(
                        Where(ProductModel.id == product.id),
                        Options(
                            selectinload(ProductModel.variations),
                            selectinload(ProductModel.variations).selectinload(
                                VariationValueModel.type
                            ),
                        ),
                        session=session,
                    )

                    await crud.bundlable_variations_values.insert.many(
                        Values(
                            [
                                {
                                    BundlableVariationValueModel.product_id: product.id,
                                    BundlableVariationValueModel.variation_value_id: product_variation.id,
                                    BundlableVariationValueModel.variation_type_id: product_variation.type.id,
                                    BundlableVariationValueModel.bundle_id: bundle.id,
                                    BundlableVariationValueModel.amount: randint(1, 10),
                                }
                                for product_variation in product_raw[0].variations
                            ]
                        ),
                        Returning(BundlableVariationValueModel),
                        session=session,
                    )

                    bundle_variation_pod = await crud.bundles_variations_pods.insert.one(
                        Returning(BundleVariationPodModel),
                        session=session,
                    )

                    bundle_variations_count = len(product_raw[0].variations)
                    product_variations_gen = entities_generator(
                        entities=product_raw[0].variations,
                        count=bundle_variations_count,
                    )
                    await crud.bundles_variations.insert.many(
                        Values(
                            [
                                {
                                    BundleVariationModel.bundle_id: bundle.id,
                                    BundleVariationModel.bundle_variation_pod_id: bundle_variation_pod.id,
                                    BundleVariationModel.product_variation_value_id: (
                                        await crud.variation_values_to_products.select.one(
                                            Where(
                                                VariationValueToProductModel.product_id
                                                == product.id,
                                                VariationValueToProductModel.variation_value_id
                                                == next(product_variations_gen).id,
                                            ),
                                            session=session,
                                        )
                                    ).id,
                                }
                                for _ in range(bundle_variations_count)
                            ]
                        ),
                        Returning(BundleVariationModel),
                        session=session,
                    )

                    await crud.bundles_pods_prices.insert.many(
                        Values(
                            [
                                {
                                    BundlePodPriceModel.product_id: product.id,
                                    BundlePodPriceModel.bundle_variation_pod_id: bundle_variation_pod.id,
                                    BundlePodPriceModel.min_quantity: (
                                        min_quantity := randint(100, 200)
                                    ),
                                    BundlePodPriceModel.value: min_quantity * uniform(1.5, 2.5),
                                    BundlePodPriceModel.discount: uniform(0.0, 1.0),
                                    BundlePodPriceModel.start_date: self.faker.date_time_this_decade(),
                                    BundlePodPriceModel.end_date: self.faker.date_time_this_decade(),
                                }
                                for _ in range(randint(1, 6))
                            ]
                        ),
                        Returning(BundlePodPriceModel),
                        session=session,
                    )

    async def load(self, size: int = 1) -> None:
        await super(ProductsPricesGenerator, self).load(size=size)


class DefaultUsersGenerator(BaseGenerator):
    supplier_counter: int = 0
    seller_counter: int = 0

    def get_supplier_counter(self) -> str:
        value = str(self.supplier_counter) if self.supplier_counter else str()
        self.supplier_counter += 1
        return value

    def get_seller_counter(self) -> str:
        value = str(self.seller_counter) if self.seller_counter else str()
        self.seller_counter += 1
        return value

    async def _load(self, session: AsyncSession) -> None:
        countries = await entities(session=session, orm_model=CountryModel)

        for _ in range(population_settings.SUPPLIERS_COUNT):
            supplier_user = await crud.users.insert.one(
                Values(
                    {
                        UserModel.is_deleted: False,
                        UserModel.is_supplier: True,
                        UserModel.email: f"{population_settings.SUPPLIER_EMAIL_LOCAL}{self.get_supplier_counter()}@{population_settings.EMAIL_DOMAIN}",
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
                        UserCredentialsModel.password: hash_password(
                            population_settings.DEFAULT_PASSWORD
                        ),
                    }
                ),
                Returning(UserCredentialsModel.id),
                session=session,
            )

        for _ in range(population_settings.SELLERS_COUNT):
            seller_user = await crud.users.insert.one(
                Values(
                    {
                        UserModel.is_deleted: False,
                        UserModel.email: f"{population_settings.SELLER_EMAIL_LOCAL}{self.get_seller_counter()}@{population_settings.EMAIL_DOMAIN}",
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
                        UserCredentialsModel.password: hash_password(
                            population_settings.DEFAULT_PASSWORD
                        ),
                    }
                ),
                Returning(UserCredentialsModel.id),
                session=session,
            )

    async def load(self, size: int = 100) -> None:
        await super(DefaultUsersGenerator, self).load(size=1)


# class OrderGenerator(BaseGenerator):
#     async def _load(self, session: AsyncSession) -> None:
#         order_statuses, sellers = (
#             await entities(session=session, orm_model=OrderStatusModel),
#             await entities(session=session, orm_model=SellerModel),
#         )

#         await crud.orders.insert.one(
#             Values(
#                 {
#                     OrderModel.datetime: datetime.now(),
#                     OrderModel.is_cart: choice([True, False]),
#                     OrderModel.seller_id: choice(sellers).id,
#                     OrderModel.status_id: choice(order_statuses).id,
#                 },
#             ),
#             Returning(OrderModel.id),
#             session=session,
#         )


# class ProductPropertyValueGenerator(BaseGenerator):
#     async def _load(self, session: AsyncSession) -> None:
#         properties = await entities(session=session, orm_model=PropertyValueModel)

#         for product in await entities(session=session, orm_model=ProductModel):
#             await crud.products_property_values.insert.one(
#                 Values(
#                     {
#                         PropertyValueToProductModel.product_id: product.id,
#                         PropertyValueToProductModel.property_value_id: choice(properties).id,
#                     }
#                 ),
#                 Returning(PropertyValueToProductModel.id),
#                 session=session,
#             )

#     async def load(self, size: int = 100) -> None:
#         await super(ProductPropertyValueGenerator, self).load(size=1)


# class StockGenerator(BaseGenerator):
#     async def _load(self, session: AsyncSession) -> None:
#         colors, sizes = await crud.categories_variation_values.select.many(
#             Where(VariationValueModel.variation_type_id == 1),
#             session=session,
#         ), await crud.categories_variation_values.select.many(
#             Where(VariationValueModel.variation_type_id == 2),
#             session=session,
#         )

#         products = await entities(session=session, orm_model=ProductModel)

#         color, size, product = choice(colors), choice(sizes), choice(products).id

#         (
#             product_variation_color,
#             product_variation_size,
#         ) = await crud.products_variation_values.insert.many(
#             Values(
#                 [
#                     {
#                         VariationValueToProductModel.product_id: product,
#                         VariationValueToProductModel.variation_value_id: color.id,
#                     },
#                     {
#                         VariationValueToProductModel.product_id: product,
#                         VariationValueToProductModel.variation_value_id: size.id,
#                     },
#                 ],
#             ),
#             Returning(VariationValueToProductModel.id),
#             session=session,
#         )


class CompanyGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        suppliers = await entities(session=session, orm_model=SupplierModel)
        countries = await country_entities(session=session, orm_model=CountryModel)
        supplier = await crud.suppliers.select.one(
            Where(SupplierModel.id == choice(suppliers).id),
            Options(joinedload(SupplierModel.company)),
            session=session,
        )

        employee_numbers = await entities(session=session, orm_model=EmployeesNumberModel)

        if not supplier.company:
            company_id = await crud.companies.insert.one(
                Values(
                    {
                        CompanyModel.name: self.faker.company(),
                        CompanyModel.country_id: choice(countries).id,
                        CompanyModel.description: self.faker.paragraph(nb_sentences=10),
                        CompanyModel.business_email: f"{randint(1, 1_000_000)}{self.faker.email()}",
                        CompanyModel.supplier_id: supplier.id,
                        CompanyModel.employees_number_id: choice(employee_numbers).id,
                        CompanyModel.is_manufacturer: choice([True, False]),
                        CompanyModel.year_established: randint(1970, 2022),
                        CompanyModel.address: self.faker.address(),
                        CompanyModel.logo_url: self.faker.image_url(),
                        # CompanyModel.business_sector: self.faker.paragraph(nb_sentences=1)[:30],
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


@dataclass(
    repr=False,
    eq=True,
    frozen=True,
    order=True,
)
class Generator:
    default_users_generator: DefaultUsersGenerator = DefaultUsersGenerator()
    product_price_generator: ProductsPricesGenerator = ProductsPricesGenerator()
    # order_generator: OrderGenerator = OrderGenerator()
    company_generator: CompanyGenerator = CompanyGenerator()
    # stock_generator: StockGenerator = StockGenerator()
    # product_property_value_generator: ProductPropertyValueGenerator = (
    #     ProductPropertyValueGenerator()
    # )

    async def setup(self) -> None:
        for field in fields(self):
            await getattr(Generator, field.name).load()


generator = Generator()
