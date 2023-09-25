from __future__ import annotations

import abc
from dataclasses import dataclass, fields
from datetime import timedelta
from random import choice, choices, randint, sample, uniform
from typing import Any, List, Type, TypeVar

from corecrud import Join, Options, Returning, SelectFrom, Values, Where
from faker import Faker
from phone_gen import PhoneNumber
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.app import crud
from core.security import hash_password
from enums import OrderStatus as OrderStatusEnum
from orm import (
    BrandModel,
    BundlableVariationValueModel,
    BundleModel,
    BundleProductVariationValueModel,
    BundleVariationPodAmountModel,
    BundleVariationPodModel,
    BundleVariationPodPriceModel,
    CategoryModel,
    CompanyModel,
    CompanyPhoneModel,
    CountryModel,
    EmployeesNumberModel,
    OrderModel,
    OrderStatusHistoryModel,
    OrderStatusModel,
    ProductImageModel,
    ProductModel,
    ProductTagModel,
    PropertyValueModel,
    PropertyValueToProductModel,
    SellerImageModel,
    SellerModel,
    SellerNotificationsModel,
    SupplierModel,
    SupplierNotificationsModel,
    TagModel,
    UserCredentialsModel,
    UserModel,
    VariationTypeModel,
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


async def variation_types_entities(session: AsyncSession, category_id: int) -> List[Any]:
    return await crud.variation_types.select.many_unique(
        Where(CategoryModel.id == category_id),
        Join(VariationTypeModel.category),
        nested_select=[VariationTypeModel.id],
        session=session,
    )


async def variation_values_entities(
    session: AsyncSession, variation_type_ids: List[int]
) -> List[Any]:
    return await crud.variation_values.select.many(
        Where(VariationValueModel.variation_type_id.in_(variation_type_ids)),
        session=session,
    )


def entities_generator(entities: List[Any], count: int = 0):
    yield from sample(entities, count or len(entities))


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
        category_properties = await entities(session=session, orm_model=PropertyValueModel)

        tags = await crud.tags.insert.many(
            Values([{TagModel.name: self.faker.sentence(nb_words=1)} for _ in range(50)]),
            Returning(TagModel),
            session=session,
        )

        for supplier in suppliers:
            for category in categories:
                if supplier.id == 1 and category.id == 3:
                    continue
                category_variation_types = await variation_types_entities(
                    session=session, category_id=category.id
                )
                category_variation_type_ids = [
                    category_variation_type.id
                    for category_variation_type in category_variation_types
                ]
                category_variation_values = await variation_values_entities(
                    session=session,
                    variation_type_ids=category_variation_type_ids,
                )
                product_count = randint(0, population_settings.PRODUCTS_COUNT_RANGE)
                for _ in range(product_count):
                    product = await crud.products.insert.one(
                        Values(
                            {
                                ProductModel.name: self.faker.sentence(nb_words=randint(1, 4)),
                                ProductModel.description: self.faker.sentence(nb_words=10),
                                ProductModel.category_id: category.id,
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

                    property_values_to_products_count = randint(5, 10)
                    property_values_gen = entities_generator(
                        entities=category_properties,
                        count=property_values_to_products_count,
                    )
                    await crud.property_values_to_products.insert.many(
                        Values(
                            [
                                {
                                    PropertyValueToProductModel.product_id: product.id,
                                    PropertyValueToProductModel.property_value_id: next(
                                        property_values_gen
                                    ).id,
                                }
                                for _ in range(property_values_to_products_count)
                            ]
                        ),
                        Returning(PropertyValueToProductModel),
                        session=session,
                    )

                    variation_values_to_products_count = randint(5, 10)
                    category_variations_gen = entities_generator(
                        entities=category_variation_values,
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
                            }
                        ),
                        Returning(BundleModel),
                        session=session,
                    )

                    random_product_variation_type = choice(category_variation_types)

                    product_variation_values = (
                        (
                            await session.execute(
                                select(VariationValueToProductModel)
                                .where(
                                    VariationTypeModel.id == random_product_variation_type.id,
                                    VariationValueToProductModel.product_id == product.id,
                                )
                                .join(
                                    VariationValueModel,
                                    VariationValueToProductModel.variation_value_id
                                    == VariationValueModel.id,
                                )
                                .join(
                                    VariationTypeModel,
                                    VariationValueModel.variation_type_id == VariationTypeModel.id,
                                )
                            )
                        )
                        .scalars()
                        .unique()
                        .all()
                    )

                    #! sometimes product_variation_values is empty
                    if not product_variation_values:
                        continue

                    await crud.bundlable_variations_values.insert.many(
                        Values(
                            [
                                {
                                    BundlableVariationValueModel.variation_value_to_product_id: product_variation_value.id,
                                    BundlableVariationValueModel.bundle_id: bundle.id,
                                    BundlableVariationValueModel.amount: randint(1, 10),
                                }
                                for product_variation_value in product_variation_values
                            ]
                        ),
                        Returning(BundlableVariationValueModel),
                        session=session,
                    )

                    product_variation_values = await crud.variation_values.select.many_unique(
                        Where(
                            ProductModel.id == product.id,
                            VariationTypeModel.id
                            == next(
                                filter(
                                    lambda x: x.id != random_product_variation_type.id,
                                    category_variation_types,
                                )
                            ).id,
                        ),
                        Join(VariationValueModel.product_variation),
                        Join(VariationValueToProductModel.product),
                        Join(VariationValueModel.type),
                        Options(
                            selectinload(VariationValueModel.product_variation).selectinload(
                                VariationValueToProductModel.product
                            ),
                            selectinload(VariationValueModel.type),
                        ),
                        session=session,
                    )
                    product_variations_gen = entities_generator(
                        entities=product_variation_values,
                    )
                    for product_variation in product_variations_gen:
                        bundle_variation_pod = await crud.bundles_variations_pods.insert.one(
                            Values(
                                {
                                    BundleVariationPodModel.product_id: product.id,
                                }
                            ),
                            Returning(BundleVariationPodModel),
                            session=session,
                        )

                        await crud.bundles_variations.insert.one(
                            Values(
                                {
                                    BundleProductVariationValueModel.bundle_id: bundle.id,
                                    BundleProductVariationValueModel.bundle_variation_pod_id: bundle_variation_pod.id,
                                    BundleProductVariationValueModel.variation_value_to_product_id: (
                                        await crud.variation_values_to_products.select.one(
                                            Where(
                                                VariationValueToProductModel.product_id
                                                == product.id,
                                                VariationValueToProductModel.variation_value_id
                                                == product_variation.id,
                                            ),
                                            session=session,
                                        )
                                    ).id,
                                }
                            ),
                            Returning(BundleProductVariationValueModel),
                            session=session,
                        )

                    bundle_pod_end_date = None
                    bundle_pod_price_count = randint(2, 10)
                    await crud.bundles_pods_prices.insert.many(
                        Values(
                            [
                                {
                                    BundleVariationPodPriceModel.bundle_variation_pod_id: bundle_variation_pod.id,
                                    BundleVariationPodPriceModel.min_quantity: (
                                        min_quantity := randint(100, 200)
                                    ),
                                    BundleVariationPodPriceModel.value: min_quantity
                                    * uniform(1.5, 2.5),
                                    BundleVariationPodPriceModel.discount: uniform(0.0, 1.0),
                                    BundleVariationPodPriceModel.start_date: (
                                        bundle_pod_start_date := bundle_pod_end_date
                                        or self.faker.date_time_this_decade()
                                    ),
                                    BundleVariationPodPriceModel.end_date: (
                                        bundle_pod_end_date := self.faker.date_time_between_dates(
                                            datetime_start=bundle_pod_start_date
                                            + timedelta(days=1),
                                            datetime_end=bundle_pod_start_date
                                            + timedelta(days=14),
                                        )
                                    )
                                    if not i == bundle_pod_price_count - 1
                                    else None,
                                }
                                for i in range(bundle_pod_price_count)
                            ]
                        ),
                        Returning(BundleVariationPodPriceModel),
                        session=session,
                    )

    async def load(self, size: int = 1) -> None:
        await super(ProductsPricesGenerator, self).load(size=size)


class SellerOrdersGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        bundle_variation_pods = await entities(session=session, orm_model=BundleVariationPodModel)
        sellers = await entities(session=session, orm_model=SellerModel)

        await crud.orders_statuses.insert.many(
            Values(
                [
                    {
                        OrderStatusModel.name: order_status.value,
                        OrderStatusModel.title: order_status.name.lower()
                        .replace("_", " ")
                        .capitalize(),
                    }
                    for order_status in list(OrderStatusEnum)
                ]
            ),
            Returning(OrderStatusModel),
            session=session,
        )

        for seller in sellers:
            orders_count = randint(0, 30)
            orders = await crud.orders.insert.many(
                Values(
                    [
                        {
                            OrderModel.seller_id: seller.id,
                            OrderModel.is_cart: choices(
                                population=[True, False], weights=[30, 70], k=1
                            )[0],
                        }
                        for _ in range(orders_count)
                    ]
                ),
                Returning(OrderModel),
                session=session,
            )

            orders_generator: List[OrderModel] = entities_generator(
                entities=orders,
            )
            for order in orders_generator:
                bundle_variation_pods_count = randint(1, 20)
                bundle_variation_pods_generator = entities_generator(
                    entities=bundle_variation_pods,
                    count=bundle_variation_pods_count,
                )
                await crud.bundles_variations_pods_amount.insert.many(
                    Values(
                        [
                            {
                                BundleVariationPodAmountModel.order_id: order.id,
                                BundleVariationPodAmountModel.bundle_variation_pod_id: bundle_variation_pod.id,
                                BundleVariationPodAmountModel.amount: randint(1, 300),
                            }
                            for bundle_variation_pod in bundle_variation_pods_generator
                        ]
                    ),
                    Returning(BundleVariationPodAmountModel),
                    session=session,
                )
                if not order.is_cart:
                    await session.execute(
                        insert(OrderStatusHistoryModel).values(
                            [
                                {
                                    OrderStatusHistoryModel.order_id: order.id,
                                    OrderStatusHistoryModel.order_status_id: (
                                        select(OrderStatusModel.id)
                                        .where(
                                            OrderStatusModel.name
                                            == list(OrderStatusEnum)[i + 1].value
                                        )
                                        .scalar_subquery()
                                    ),
                                }
                                for i in range(randint(1, 5))
                            ]
                        )
                    )

    async def load(self, size: int = 1) -> None:
        await super(SellerOrdersGenerator, self).load(size=size)


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
    seller_orders_generator: SellerOrdersGenerator = SellerOrdersGenerator()
    company_generator: CompanyGenerator = CompanyGenerator()
    # stock_generator: StockGenerator = StockGenerator()
    # product_property_value_generator: ProductPropertyValueGenerator = (
    #     ProductPropertyValueGenerator()
    # )

    async def setup(self) -> None:
        for field in fields(self):
            await getattr(Generator, field.name).load()


generator = Generator()
