from __future__ import annotations

from collections.abc import Generator, Sequence
from csv import DictWriter
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

from .settings import (
    BUNDLABLE_VARIATION_VALUES_CSV_PATH,
    BUNDLE_PRICES_CSV_PATH,
    BUNDLES_CVS_PATH,
    PRODUCT_IMAGES_CSV_PATH,
    PRODUCT_PRICES_CSV_PATH,
    PRODUCT_TAGS_CSV_PATH,
    PRODUCT_VARIATION_PRICES_CSV_PATH,
    PRODUCT_VARIATION_VALUES_CSV_PATH,
    PRODUCTS_CSV_PATH,
    PROPERTY_VALUES_TO_PRODUCTS_CSV_PATH,
    VARIATION_IMAGES_CSV_PATH,
    population_settings,
)


@dataclass(slots=True)
class CsvGenerator:
    categories: Sequence[CategoryModel]
    suppliers: Sequence[SupplierModel]
    brands: Sequence[BrandModel]
    tags: Sequence[TagModel]
    category_properties: Sequence[PropertyValueModel]
    category_variation_values: dict[int, Sequence[VariationValueModel]]
    variation_values: Sequence[VariationValueModel]

    _products: list[dict[str, Any]] | None = None
    _product_prices_data: list[dict[str, Any]] | None = None
    _bundle_data: list[dict[str, Any]] | None = None
    _product_variation_values_data: list[dict[str, Any]] | None = None
    _product_variation_price_data: list[dict[str, Any]] | None = None
    _assigned_bundle_variation_types: list[int] | None = None

    faker: Faker = Faker()

    def generate_csv_content(self) -> None:
        self.__products(
            csv_file_path=PRODUCTS_CSV_PATH,
        )
        self.__product_prices(
            csv_file_path=PRODUCT_PRICES_CSV_PATH,
        )
        self.__product_images(
            csv_file_path=PRODUCT_IMAGES_CSV_PATH,
        )
        self.__product_tags(
            csv_file_path=PRODUCT_TAGS_CSV_PATH,
        )
        self.__property_values_to_products(
            csv_file_path=PROPERTY_VALUES_TO_PRODUCTS_CSV_PATH,
        )
        self.__product_variations(
            product_variations_csv_file_path=PRODUCT_VARIATION_VALUES_CSV_PATH,
            variation_images_csv_file_path=VARIATION_IMAGES_CSV_PATH,
            product_variations_prices_csv_file_path=PRODUCT_VARIATION_PRICES_CSV_PATH,
        )
        self.__bundles(
            csv_file_path=BUNDLES_CVS_PATH,
        )
        self.__bundle_variations(
            bunlable_variations_csv_file_path=BUNDLABLE_VARIATION_VALUES_CSV_PATH,
            bundle_prices_csv_file_path=BUNDLE_PRICES_CSV_PATH,
        )
        self.__bundle_variation_pods(
            bundle_pod_csb_file_path="",
            bundle_variation_pods_csv_file_path="",
            bundle_pod_prices_csv_file_path="",
        )

    def __write_data(self, csv_file_path: str, data: list[dict[str, Any]]) -> None:
        fields = data[0].keys()
        with open(csv_file_path, "w", newline="") as csv:
            writer = DictWriter(csv, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)

    def __entities_generator(self, entities: List[Any], count: int = 0) -> Generator:
        yield from sample(entities, count or len(entities))

    def __get_image_url(self, width: int, height: int) -> str:
        urls = [
            "https://place.dog/{width}/{height}".format(width=width, height=height),
            "https://picsum.photos/id/{image}/{width}/{height}".format(
                width=width, height=height, image=randint(1, 500)
            ),
        ]
        return choice(urls)

    def __get_squared_image_thumbnail_urls(self, sizes: list[tuple[int, int]]) -> dict[str, Any]:
        return {f"thumbnail_{size[0]}": self.__get_image_url(*size) for size in sizes}

    def __products(self, csv_file_path: str) -> None:
        product_data = []

        id_auto_increment = 1

        for supplier in self.suppliers:
            for category in self.categories:
                if supplier.id == 1 and category.id == 3:
                    continue
                product_count = randint(0, population_settings.PRODUCTS_COUNT_RANGE)
                for _ in range(product_count):
                    create_update_datetime = self.faker.date_this_decade()
                    product_data.append(
                        {
                            "id": id_auto_increment,
                            "name": self.faker.sentence(nb_words=randint(1, 4)).strip("."),
                            "description": self.faker.sentence(nb_words=10),
                            "supplier_id": supplier.id,
                            "category_id": category.id,
                            "grade_average": uniform(0.0, 5.0),
                            "is_active": True,
                            "brand_id": choice(self.brands).id,
                            "created_at": create_update_datetime,
                            "updated_at": create_update_datetime,
                        }
                    )
                    id_auto_increment += 1

        self.__write_data(
            csv_file_path=csv_file_path,
            data=product_data,
        )

        self._products = product_data

    def __product_prices(self, csv_file_path: str) -> None:
        product_price_data = []

        id_auto_increment = 1

        for product in self._products:
            product_price_data.append(
                {
                    "id": id_auto_increment,
                    "value": uniform(0.50, 10.00),
                    "discount": uniform(0.0, 1.0),
                    "start_date": self.faker.date_this_decade(),
                    "end_date": self.faker.date_this_decade(),
                    "min_quantity": randint(10, 20),
                    "product_id": product["id"],
                }
            )
            id_auto_increment += 1

        self.__write_data(
            csv_file_path=csv_file_path,
            data=product_price_data,
        )

        self._product_prices_data = product_price_data

    def __product_images(self, csv_file_path: str) -> None:
        product_images_data = []
        id_auto_increment = 1

        for product in self._products:
            for i in range(randint(1, 10)):
                product_images_data.append(
                    {
                        "id": id_auto_increment,
                        "product_id": product["id"],
                        "image_url": self.faker.image_url(
                            placeholder_url=self.__get_image_url(width=900, height=900)
                        ),
                        "thumbnail_urls": self.__get_squared_image_thumbnail_urls(
                            sizes=upload_file_settings.PRODUCT_THUMBNAIL_PROPERTIES
                        ),
                        "order": i,
                    }
                )
                id_auto_increment += 1

        self.__write_data(
            csv_file_path=csv_file_path,
            data=product_images_data,
        )

    def __product_tags(self, csv_file_path: str) -> None:
        product_tags_data = []
        id_auto_increment = 1

        for product in self._products:
            for _ in range(randint(1, 10)):
                product_tags_data.append(
                    {
                        "id": id_auto_increment,
                        "product_id": product["id"],
                        "tag_id": choice(self.tags).id,
                    }
                )
                id_auto_increment += 1

        self.__write_data(
            csv_file_path=csv_file_path,
            data=product_tags_data,
        )

    def __property_values_to_products(self, csv_file_path: str) -> None:
        property_values_to_products_data = []
        id_auto_increment = 1

        property_values_to_products_count = randint(5, 10)
        property_values_gen = self.__entities_generator(
            entities=self.category_properties,
            count=property_values_to_products_count,
        )

        for product in self._products:
            for property_value in property_values_gen:
                property_values_to_products_data.append(
                    {
                        "id": id_auto_increment,
                        "product_id": product["id"],
                        "property_value_id": property_value.id,
                        "optional_value": f"{randint(10, 50)}%"
                        if property_value.type.has_optional_value
                        else None,
                    }
                )
                id_auto_increment += 1

        self.__write_data(
            csv_file_path=csv_file_path,
            data=property_values_to_products_data,
        )

    def __product_variations(
        self,
        product_variations_csv_file_path: str,
        variation_images_csv_file_path: str,
        product_variations_prices_csv_file_path: str,
    ) -> None:
        """
        Includes variation values, variation images and variation prices.
        """

        product_variation_values_data = []
        variation_images_data = []
        product_variation_prices_data = []

        product_variation_values_id_auto_increment = 1
        variation_image_id_auto_increment = 1
        product_variation_prices_id_auto_increment = 1

        for product in self._products:
            variation_values_to_products_count = randint(5, 10)
            category_variations_gen = self.__entities_generator(
                entities=self.category_variation_values[product["category_id"]],
                count=variation_values_to_products_count,
            )
            for category_variation in category_variations_gen:
                product_variation_values_data.append(
                    {
                        "id": product_variation_values_id_auto_increment,
                        "product_id": product["id"],
                        "variation_value_id": category_variation.id,
                    }
                )

                image = self.__get_image_url(width=220, height=220)

                for _ in range(randint(1, 5)):
                    variation_images_data.append(
                        {
                            "id": variation_image_id_auto_increment,
                            "image_url": image,
                            "thumbnail_url": image,
                            "variation_value_to_product_id": product_variation_values_id_auto_increment,
                        }
                    )

                multiplier = uniform(0.1, 2.0)
                product_price = self._product_prices_data[product["id"] - 1]["value"]

                product_variation_prices_data.append(
                    {
                        "id": product_variation_prices_id_auto_increment,
                        "variation_value_to_product_id": product_variation_values_id_auto_increment,
                        "value": float(product_price) * multiplier,
                        "multiplier": multiplier,
                        "discount": uniform(0.0, 1.0),
                        "start_date": self.faker.date_this_decade(),
                        "end_date": self.faker.date_this_decade(),
                        "min_quantity": randint(10, 20),
                    }
                )

                product_variation_values_id_auto_increment += 1
                variation_image_id_auto_increment += 1
                product_variation_prices_id_auto_increment += 1

        self.__write_data(
            csv_file_path=product_variations_csv_file_path,
            data=product_variation_values_data,
        )
        self.__write_data(
            csv_file_path=variation_images_csv_file_path,
            data=variation_images_data,
        )
        self.__write_data(
            csv_file_path=product_variations_prices_csv_file_path,
            data=product_variation_prices_data,
        )

        self._product_variation_values_data = product_variation_values_data
        self._product_variation_price_data = product_variation_prices_data

    def __bundles(self, csv_file_path: str) -> None:
        bundle_data = []
        id_auto_increment = 1

        for product in self._products:
            bundle_data.append(
                {
                    "id": id_auto_increment,
                    "product_id": product["id"],
                }
            )

            id_auto_increment += 1

        self.__write_data(
            csv_file_path=csv_file_path,
            data=bundle_data,
        )

        self._bundle_data = bundle_data

    def __bundle_variations(
        self,
        bunlable_variations_csv_file_path: str,
        bundle_prices_csv_file_path: str,
    ):
        assigned_bundle_variation_types = []

        bundlable_variation_values_data = []
        bundle_price_data = []

        bundlable_variation_id_auto_increment = 1
        bundle_price_id_auto_increment = 1

        for product in self._products:
            variation_value_to_product_ids_to_variation_value_ids = {}

            for product_variation_value in self._product_variation_values_data:
                if product_variation_value["product_id"] == product["id"]:
                    variation_value_to_product_ids_to_variation_value_ids[
                        product_variation_value["id"]
                    ] = product_variation_value["variation_value_id"]

            product_variation_values_to_types = {}

            for variation_value in self.variation_values:
                if (
                    variation_value.id
                    in variation_value_to_product_ids_to_variation_value_ids.values()
                ):
                    if variation_value.variation_type_id not in product_variation_values_to_types:
                        product_variation_values_to_types[variation_value.variation_type_id] = [
                            variation_value.id
                        ]
                    else:
                        product_variation_values_to_types[
                            variation_value.variation_type_id
                        ].append(variation_value.id)

            random_product_variation_type_id = choice(
                list(product_variation_values_to_types.keys())
            )
            assigned_bundle_variation_types.append(random_product_variation_type_id)

            random_type_variation_values_to_product_ids = [
                ids[0]
                for ids in variation_value_to_product_ids_to_variation_value_ids.items()
                if ids[1] in product_variation_values_to_types[random_product_variation_type_id]
            ]

            base_bundle_price = 0
            bundle_product_amount = 0

            for variation_value_to_product_id in random_type_variation_values_to_product_ids:
                product_amount = randint(1, 10)
                bundlable_variation_values_data.append(
                    {
                        "id": bundlable_variation_id_auto_increment,
                        "variation_value_to_product_id": variation_value_to_product_id,
                        "bundle_id": self._bundle_data[product["id"] - 1]["id"],
                        "amount": product_amount,
                    }
                )

                bundlable_variation_id_auto_increment += 1

                product_variation_price = [
                    product_variation_price
                    for product_variation_price in self._product_variation_price_data
                    if product_variation_price["variation_value_to_product_id"]
                    == variation_value_to_product_id
                ][0]
                base_bundle_price += product_variation_price["value"] * (
                    1 - product_variation_price["discount"]
                )
                bundle_product_amount += product_amount

            bundle_price_data.append(
                {
                    "id": bundle_price_id_auto_increment,
                    "bundle_id": self._bundle_data[product["id"] - 1]["id"],
                    "price": base_bundle_price,
                    "discount": uniform(0.0, 0.4),
                    "start_date": (start_date := datetime.now()),
                    "end_date": start_date + timedelta(days=30),
                    "min_quantity": 100,
                }
            )

            bundle_price_id_auto_increment += 1

        self.__write_data(
            csv_file_path=bunlable_variations_csv_file_path,
            data=bundlable_variation_values_data,
        )
        self.__write_data(
            csv_file_path=bundle_prices_csv_file_path,
            data=bundle_price_data,
        )

        self._assigned_bundle_variation_types = set(assigned_bundle_variation_types)

    def __bundle_variation_pods(
        self,
        bundle_pod_csb_file_path: str,
        bundle_variation_pods_csv_file_path: str,
        bundle_pod_prices_csv_file_path: str,
    ) -> None:
        bundle_pods_data = []
        bundle_pod_variations_data = []
        bundle_pod_prices_data = []

        print(self._assigned_bundle_variation_types)
