from __future__ import annotations

import abc
from dataclasses import dataclass, fields
from datetime import datetime, timedelta
from random import choice, choices, randint, sample, uniform
from typing import Any, List, Type, TypeVar

# from icecream import ic
from faker import Faker
from phone_gen import PhoneNumber
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from core.security import hash_password
from core.settings import upload_file_settings
from enums import OrderStatus as OrderStatusEnum
from orm import (
    BrandModel,
    BundlableVariationValueModel,
    BundleModel,
    BundlePriceModel,
    BundleProductVariationValueModel,
    BundleVariationPodAmountModel,
    BundleVariationPodModel,
    BundleVariationPodPriceModel,
    CategoryModel,
    CompanyBusinessSectorToCategoryModel,
    CompanyModel,
    CompanyPhoneModel,
    CountryModel,
    EmployeesNumberModel,
    OrderModel,
    OrderStatusHistoryModel,
    OrderStatusModel,
    ProductImageModel,
    ProductModel,
    ProductPriceModel,
    ProductReviewModel,
    ProductReviewPhotoModel,
    ProductReviewReactionModel,
    ProductTagModel,
    ProductVariationPriceModel,
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
    VariationValueImageModel,
    VariationValueModel,
    VariationValueToProductModel,
)
from orm.core import ORMModel, get_async_sessionmaker
from utils.time import exec_time

from .settings import population_settings

T = TypeVar("T", bound=ORMModel)


async def entities(session: AsyncSession, orm_model: Type[T]) -> List[Any]:
    return (await session.execute(select(orm_model.id))).all()


async def category_property_entities(session: AsyncSession) -> List[Any]:
    return (
        (
            await session.execute(
                select(PropertyValueModel).options(selectinload(PropertyValueModel.type))
            )
        )
        .scalars()
        .all()
    )


async def category_entities(session: AsyncSession) -> List[Any]:
    return (
        (await session.execute(select(CategoryModel).where(CategoryModel.level == 3)))
        .scalars()
        .all()
    )


async def country_entities(session: AsyncSession) -> List[Any]:
    return (await session.execute(select(CountryModel.id, CountryModel.country))).all()


async def variation_types_entities(session: AsyncSession, category_id: int) -> List[Any]:
    return (
        await session.execute(
            select(VariationTypeModel.id)
            .where(CategoryModel.id == category_id)
            .join(VariationTypeModel.category)
        )
    ).all()


async def variation_values_entities(
    session: AsyncSession, variation_type_ids: List[int]
) -> List[Any]:
    return (
        (
            await session.execute(
                select(VariationValueModel).where(
                    VariationValueModel.variation_type_id.in_(variation_type_ids)
                )
            )
        )
        .scalars()
        .all()
    )


def entities_generator(entities: List[Any], count: int = 0):
    yield from sample(entities, count or len(entities))


def get_image_url(width: int, height: int) -> str:
    urls = [
        "https://place.dog/{width}/{height}".format(width=width, height=height),
        "https://picsum.photos/id/{image}/{width}/{height}".format(
            width=width, height=height, image=randint(1, 500)
        ),
    ]
    return choice(urls)


def get_squared_image_thumbnail_urls(sizes: list[tuple[int, int]]) -> dict[str, Any]:
    return {f"thumbnail_{size[0]}": get_image_url(*size) for size in sizes}


class BaseGenerator(abc.ABC):
    faker: Faker = Faker()

    @abc.abstractmethod
    async def _load(self, session: AsyncSession) -> None:
        ...

    @exec_time()
    async def load(self, size: int = 100) -> None:
        async def load(_obj: BaseGenerator, session: AsyncSession, _size: int) -> None:
            for _ in range(size):
                await _obj._load(session=session)

        async with get_async_sessionmaker(echo=False).begin() as _session:
            await load(_obj=self, session=_session, _size=size)


class ProductsPricesGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        categories: List[CategoryModel] = await category_entities(session=session)
        suppliers: List[SupplierModel] = await entities(session=session, orm_model=SupplierModel)
        brands: List[BrandModel] = await entities(session=session, orm_model=BrandModel)
        category_properties: List[PropertyValueModel] = await category_property_entities(
            session=session
        )

        tags = (
            (
                await session.execute(
                    insert(TagModel)
                    .values([{TagModel.name: self.faker.sentence(nb_words=1)} for _ in range(50)])
                    .returning(TagModel)
                )
            )
            .scalars()
            .all()
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
                    # * ===================== PRODUCT =====================
                    create_update_datetime = self.faker.date_this_decade()
                    product = (
                        await session.execute(
                            insert(ProductModel)
                            .values(
                                {
                                    ProductModel.name: self.faker.sentence(
                                        nb_words=randint(1, 4)
                                    ).strip("."),
                                    ProductModel.description: self.faker.sentence(nb_words=10),
                                    ProductModel.supplier_id: supplier.id,
                                    ProductModel.category_id: category.id,
                                    ProductModel.grade_average: uniform(0.0, 5.0),
                                    ProductModel.is_active: True,
                                    ProductModel.brand_id: choice(brands).id,
                                    ProductModel.created_at: create_update_datetime,
                                    ProductModel.updated_at: create_update_datetime,
                                },
                            )
                            .returning(ProductModel)
                        )
                    ).scalar_one()

                    # * ===================== PRODUCT PRICE =====================
                    product_price = (
                        await session.execute(
                            insert(ProductPriceModel)
                            .values(
                                {
                                    ProductPriceModel.value: uniform(0.50, 10.00),
                                    ProductPriceModel.discount: uniform(0.0, 1.0),
                                    ProductPriceModel.start_date: self.faker.date_this_decade(),
                                    ProductPriceModel.end_date: self.faker.date_this_decade(),
                                    ProductPriceModel.min_quantity: randint(10, 20),
                                    ProductPriceModel.product_id: product.id,
                                }
                            )
                            .returning(ProductPriceModel)
                        )
                    ).scalar_one()

                    # * ===================== PRODUCT IMAGES =====================
                    await session.execute(
                        insert(ProductImageModel).values(
                            [
                                {
                                    ProductImageModel.product_id: product.id,
                                    ProductImageModel.image_url: self.faker.image_url(
                                        placeholder_url=get_image_url(width=900, height=900)
                                    ),
                                    ProductImageModel.thumbnail_urls: get_squared_image_thumbnail_urls(
                                        sizes=upload_file_settings.PRODUCT_THUMBNAIL_PROPERTIES
                                    ),
                                    ProductImageModel.order: i,
                                }
                                for i in range(randint(1, 10))
                            ]
                        )
                    )

                    # * ===================== PRODUCT TAGS =====================
                    await session.execute(
                        insert(ProductTagModel).values(
                            [
                                {
                                    ProductTagModel.product_id: product.id,
                                    ProductTagModel.tag_id: choice(tags).id,
                                }
                                for _ in range(randint(1, 10))
                            ]
                        )
                    )

                    # * ===================== PROPERTY VALUES TO PRODUCTS =====================
                    property_values_to_products_count = randint(5, 10)
                    property_values_gen = entities_generator(
                        entities=category_properties,
                        count=property_values_to_products_count,
                    )

                    await session.execute(
                        insert(PropertyValueToProductModel).values(
                            [
                                {
                                    PropertyValueToProductModel.product_id: product.id,
                                    PropertyValueToProductModel.property_value_id: property_value.id,
                                    PropertyValueToProductModel.optional_value: f"{randint(10, 50)}%"
                                    if property_value.type.has_optional_value
                                    else None,
                                }
                                for property_value in property_values_gen
                            ]
                        )
                    )

                    # * ===================== VARIATION VALUES TO PRODUCT + PRODUCT VARIATION PRICES + VARIATION VALUE IMAGES =====================
                    variation_values_to_products_count = randint(5, 10)
                    category_variations_gen = entities_generator(
                        entities=category_variation_values,
                        count=variation_values_to_products_count,
                    )
                    for category_variation in category_variations_gen:
                        product_variation_value = (
                            await session.execute(
                                insert(VariationValueToProductModel)
                                .values(
                                    {
                                        VariationValueToProductModel.product_id: product.id,
                                        VariationValueToProductModel.variation_value_id: category_variation.id,
                                    }
                                )
                                .returning(VariationValueToProductModel)
                            )
                        ).scalar_one()

                        image = get_image_url(width=220, height=220)
                        await session.execute(
                            insert(VariationValueImageModel).values(
                                [
                                    {
                                        VariationValueImageModel.image_url: image,
                                        VariationValueImageModel.thumbnail_url: image,
                                        VariationValueImageModel.variation_value_to_product_id: product_variation_value.id,
                                    }
                                    for _ in range(randint(1, 5))
                                ]
                            )
                        )

                        multiplier = uniform(0.1, 2.0)
                        await session.execute(
                            insert(ProductVariationPriceModel).values(
                                {
                                    ProductVariationPriceModel.variation_value_to_product_id: product_variation_value.id,
                                    ProductVariationPriceModel.value: (
                                        float(product_price.value) * multiplier
                                    ),
                                    ProductVariationPriceModel.multiplier: multiplier,
                                    ProductVariationPriceModel.discount: uniform(0.0, 1.0),
                                    ProductVariationPriceModel.start_date: self.faker.date_this_decade(),
                                    ProductVariationPriceModel.end_date: self.faker.date_this_decade(),
                                    ProductVariationPriceModel.min_quantity: randint(10, 20),
                                }
                            )
                        )

                    # * ===================== BUNDLE =====================
                    bundle = (
                        await session.execute(
                            insert(BundleModel)
                            .values(
                                {
                                    BundleModel.product_id: product.id,
                                    BundleModel.name: "Bundle1",
                                }
                            )
                            .returning(BundleModel)
                        )
                    ).scalar_one()

                    # * ===================== BUNDLABLE VARIATION VALUES =====================
                    random_product_variation_type = choice(category_variation_types)

                    product_variation_values = (
                        (
                            await session.execute(
                                select(VariationValueToProductModel)
                                .where(
                                    VariationTypeModel.id == random_product_variation_type.id,
                                    VariationValueToProductModel.product_id == product.id,
                                )
                                .join(VariationValueToProductModel.variation)
                                .join(VariationValueModel.type)
                                .options(
                                    selectinload(VariationValueToProductModel.prices),
                                    selectinload(VariationValueToProductModel.variation),
                                    selectinload(VariationValueToProductModel.product),
                                )
                            )
                        )
                        .scalars()
                        .unique()
                        .all()
                    )

                    #! sometimes product_variation_values and it's last element's prices are empty: WHAT THE FUCK?!
                    if not product_variation_values or not all(
                        [bool(p.prices) for p in product_variation_values]
                    ):
                        continue

                    base_bundle_price = 0
                    bundle_product_amount = 0

                    for product_variation_value in product_variation_values:
                        product_amount = randint(1, 10)
                        await session.execute(
                            insert(BundlableVariationValueModel).values(
                                {
                                    BundlableVariationValueModel.variation_value_to_product_id: product_variation_value.id,
                                    BundlableVariationValueModel.bundle_id: bundle.id,
                                    BundlableVariationValueModel.amount: product_amount,
                                }
                            )
                        )
                        base_bundle_price += product_variation_value.prices[0].value * (
                            1 - product_variation_value.prices[0].discount
                        )
                        bundle_product_amount += product_amount

                    await session.execute(
                        insert(BundlePriceModel).values(
                            {
                                BundlePriceModel.bundle_id: bundle.id,
                                BundlePriceModel.price: base_bundle_price,
                                BundlePriceModel.discount: uniform(0.0, 0.4),
                                BundlePriceModel.start_date: (start_date := datetime.now()),
                                BundlePriceModel.end_date: start_date + timedelta(days=30),
                                BundlePriceModel.min_quantity: 100,
                            }
                        )
                    )

                    product_variation_values = (
                        (
                            await session.execute(
                                select(VariationValueModel)
                                .where(
                                    ProductModel.id == product.id,
                                    VariationTypeModel.id
                                    == next(
                                        filter(
                                            lambda x: x.id != random_product_variation_type.id,
                                            category_variation_types,
                                        )
                                    ).id,
                                )
                                .join(VariationValueModel.product_variation)
                                .join(VariationValueToProductModel.product)
                                .join(VariationValueModel.type)
                                .options(
                                    selectinload(
                                        VariationValueModel.product_variation
                                    ).selectinload(VariationValueToProductModel.product),
                                    selectinload(
                                        VariationValueModel.product_variation
                                    ).selectinload(VariationValueToProductModel.prices),
                                    selectinload(VariationValueModel.type),
                                )
                            )
                        )
                        .scalars()
                        .unique()
                        .all()
                    )

                    product_variations_gen: List[VariationValueModel] = entities_generator(
                        entities=product_variation_values,
                    )

                    # * ===================== BUNDLE VARIATION PODS + BUNDLE POD PRICES =====================
                    for product_variation in product_variations_gen:
                        bundle_variation_pod = (
                            await session.execute(
                                insert(BundleVariationPodModel)
                                .values(
                                    {
                                        BundleVariationPodModel.product_id: product.id,
                                    }
                                )
                                .returning(BundleVariationPodModel)
                            )
                        ).scalar_one()

                        await session.execute(
                            insert(BundleProductVariationValueModel).values(
                                {
                                    BundleProductVariationValueModel.bundle_id: bundle.id,
                                    BundleProductVariationValueModel.bundle_variation_pod_id: bundle_variation_pod.id,
                                    BundleProductVariationValueModel.variation_value_to_product_id: (
                                        select(VariationValueToProductModel.id)
                                        .where(
                                            VariationValueToProductModel.product_id == product.id,
                                            VariationValueToProductModel.variation_value_id
                                            == product_variation.id,
                                        )
                                        .scalar_subquery()
                                    ),
                                }
                            )
                        )
                        bundle_pod_price = (
                            (
                                (product_price.value * (1 - product_price.discount))
                                * bundle_product_amount
                            )
                            + base_bundle_price
                            + (
                                (
                                    product_variation.product_variation.prices[0].value
                                    * (1 - product_variation.product_variation.prices[0].discount)
                                )
                                * bundle_product_amount
                            )
                        )
                        bundle_pod_end_date = None
                        await session.execute(
                            insert(BundleVariationPodPriceModel).values(
                                {
                                    BundleVariationPodPriceModel.bundle_variation_pod_id: bundle_variation_pod.id,
                                    BundleVariationPodPriceModel.value: bundle_pod_price,
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
                                    ),
                                }
                            )
                        )

    async def load(self, size: int = 1) -> None:
        await super(ProductsPricesGenerator, self).load(size=size)


class ProductReviewsGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        sellers: List[SellerModel] = await entities(session=session, orm_model=SellerModel)
        products: List[ProductModel] = await entities(session=session, orm_model=ProductModel)

        reviews: List[ProductReviewModel] = []
        for seller in sellers:
            seller_reviews = (
                (
                    await session.execute(
                        insert(ProductReviewModel)
                        .values(
                            [
                                {
                                    ProductReviewModel.text: self.faker.sentence(
                                        nb_words=randint(5, 20)
                                    ),
                                    ProductReviewModel.seller_id: seller.id,
                                    ProductReviewModel.grade_overall: randint(1, 5),
                                    ProductReviewModel.product_id: choice(products).id,
                                }
                                for _ in range(population_settings.REVIEWS_PER_SELLER_RANGE)
                            ]
                        )
                        .returning(ProductReviewModel)
                    )
                )
                .scalars()
                .all()
            )
            reviews.extend(seller_reviews)

        for review in reviews:
            url_images = [
                get_image_url(width=500, height=500)
                for _ in range(randint(1, population_settings.PHOTOS_PER_REVIEW_LIMIT))
            ]
            await session.execute(
                insert(ProductReviewPhotoModel).values(
                    [
                        {
                            ProductReviewPhotoModel.product_review_id: review.id,
                            ProductReviewPhotoModel.image_url: image_url,
                            ProductReviewPhotoModel.serial_number: serial_number,
                        }
                        for serial_number, image_url in enumerate(url_images)
                    ],
                )
            )

            for _seller in sample(sellers, randint(0, len(sellers))):
                await session.execute(
                    insert(ProductReviewReactionModel).values(
                        {
                            ProductReviewReactionModel.product_review_id: review.id,
                            ProductReviewReactionModel.reaction: choice([True, False]),
                            ProductReviewReactionModel.seller_id: _seller.id,
                        }
                    )
                )

    async def load(self, size: int = 1) -> None:
        await super(ProductReviewsGenerator, self).load(size=size)


class SellerOrdersGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        bundle_variation_pods = await entities(session=session, orm_model=BundleVariationPodModel)
        sellers = await entities(session=session, orm_model=SellerModel)

        await session.execute(
            insert(OrderStatusModel).values(
                [
                    {
                        OrderStatusModel.name: order_status.value,
                        OrderStatusModel.title: order_status.name.lower()
                        .replace("_", " ")
                        .capitalize(),
                    }
                    for order_status in list(OrderStatusEnum)
                ]
            )
        )

        for seller in sellers:
            orders_count = randint(0, 30)
            if orders_count:
                orders = (
                    (
                        await session.execute(
                            insert(OrderModel)
                            .values(
                                [
                                    {
                                        OrderModel.seller_id: seller.id,
                                        OrderModel.is_cart: choices(
                                            population=[True, False], weights=[30, 70], k=1
                                        )[0],
                                    }
                                    for _ in range(orders_count)
                                ]
                            )
                            .returning(OrderModel)
                        )
                    )
                    .scalars()
                    .fetchall()
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
                    await session.execute(
                        insert(BundleVariationPodAmountModel).values(
                            [
                                {
                                    BundleVariationPodAmountModel.order_id: order.id,
                                    BundleVariationPodAmountModel.bundle_variation_pod_id: bundle_variation_pod.id,
                                    BundleVariationPodAmountModel.amount: randint(1, 300),
                                }
                                for bundle_variation_pod in bundle_variation_pods_generator
                            ]
                        )
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
            supplier_user = (
                await session.execute(
                    insert(UserModel)
                    .values(
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
                    )
                    .returning(UserModel)
                )
            ).scalar_one()

            supplier = (
                await session.execute(
                    insert(SupplierModel)
                    .values(
                        {
                            SupplierModel.user_id: supplier_user.id,
                            SupplierModel.grade_average: 0.0,
                            SupplierModel.license_number: "3255900647702",
                            SupplierModel.additional_info: "Supplier additional info",
                        }
                    )
                    .returning(SupplierModel)
                )
            ).scalar_one()

            await session.execute(
                insert(SupplierNotificationsModel).values(
                    {SupplierNotificationsModel.supplier_id: supplier.id}
                )
            )

            await session.execute(
                insert(UserCredentialsModel).values(
                    {
                        UserCredentialsModel.user_id: supplier_user.id,
                        UserCredentialsModel.password: hash_password(
                            population_settings.DEFAULT_PASSWORD
                        ),
                    }
                )
            )

        for _ in range(population_settings.SELLERS_COUNT):
            seller_user = (
                await session.execute(
                    insert(UserModel)
                    .values(
                        {
                            UserModel.is_deleted: False,
                            UserModel.email: f"{population_settings.SELLER_EMAIL_LOCAL}{self.get_seller_counter()}@{population_settings.EMAIL_DOMAIN}",
                            UserModel.is_verified: True,
                            UserModel.first_name: "Seller Name",
                            UserModel.last_name: "Seller Lastname",
                            UserModel.phone_number: "3255900647702",
                            UserModel.country_id: choice(countries).id,
                        }
                    )
                    .returning(UserModel)
                )
            ).scalar_one()

            seller = (
                await session.execute(
                    insert(SellerModel)
                    .values({SellerModel.user_id: seller_user.id})
                    .returning(SellerModel)
                )
            ).scalar_one()

            await session.execute(
                insert(SellerImageModel).values(
                    {
                        SellerImageModel.seller_id: seller.id,
                        SellerImageModel.source_url: "https://placekitten.com/200/300",
                        SellerImageModel.thumbnail_url: "https://placekitten.com/200/300",
                    }
                )
            )

            await session.execute(
                insert(SellerNotificationsModel).values(
                    {SellerNotificationsModel.seller_id: seller.id}
                )
            )

            await session.execute(
                insert(UserCredentialsModel).values(
                    {
                        UserCredentialsModel.user_id: seller_user.id,
                        UserCredentialsModel.password: hash_password(
                            population_settings.DEFAULT_PASSWORD
                        ),
                    }
                )
            )

    async def load(self, size: int = 100) -> None:
        await super(DefaultUsersGenerator, self).load(size=1)


class CompanyGenerator(BaseGenerator):
    async def _load(self, session: AsyncSession) -> None:
        suppliers = await entities(session=session, orm_model=SupplierModel)
        countries = await country_entities(session=session)
        categories = await entities(session=session, orm_model=CategoryModel)
        supplier = (
            await session.execute(
                select(SupplierModel)
                .where(SupplierModel.id == choice(suppliers).id)
                .options(joinedload(SupplierModel.company))
            )
        ).scalar_one()

        employee_numbers = await entities(session=session, orm_model=EmployeesNumberModel)

        if not supplier.company:
            company_id = (
                await session.execute(
                    insert(CompanyModel)
                    .values(
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
                    )
                    .returning(CompanyModel.id)
                )
            ).scalar_one()

            country = choice(countries)
            await session.execute(
                insert(CompanyPhoneModel).values(
                    {
                        CompanyPhoneModel.company_id: company_id,
                        CompanyPhoneModel.country_id: country.id,
                        CompanyPhoneModel.phone_number: PhoneNumber(country.country).get_number(
                            full=False
                        ),
                    }
                )
            )

            await session.execute(
                insert(CompanyBusinessSectorToCategoryModel).values(
                    {
                        CompanyBusinessSectorToCategoryModel.company_id: company_id,
                        CompanyBusinessSectorToCategoryModel.category_id: choice(categories).id,
                    }
                )
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
    product_reviews_generator: ProductReviewsGenerator = ProductReviewsGenerator()
    # stock_generator: StockGenerator = StockGenerator()
    # product_property_value_generator: ProductPropertyValueGenerator = (
    #     ProductPropertyValueGenerator()
    # )

    async def setup(self) -> None:
        for field in fields(self):
            await getattr(Generator, field.name).load()


generator = Generator()
