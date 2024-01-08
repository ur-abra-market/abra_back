from __future__ import annotations

from collections.abc import Generator
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
    categories: list[CategoryModel]
    suppliers: list[SupplierModel]
    brands: list[BrandModel]
    tags: list[TagModel]
    category_properties: list[PropertyValueModel]
    category_variation_values: dict[int, list[VariationValueModel]]

    _products: list[dict[str, Any]] | None = None
    _product_prices_data: list[dict[str, Any]] | None = None

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

        product_id_auto_increment = 1

        for supplier in self.suppliers:
            for category in self.categories:
                if supplier.id == 1 and category.id == 3:
                    continue
                product_count = randint(0, population_settings.PRODUCTS_COUNT_RANGE)
                for _ in range(product_count):
                    create_update_datetime = self.faker.date_this_decade()
                    product_data.append(
                        {
                            "id": product_id_auto_increment,
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
                    product_id_auto_increment += 1

        self.__write_data(
            csv_file_path=csv_file_path,
            data=product_data,
        )

        self._products = product_data

    def __product_prices(self, csv_file_path: str) -> None:
        product_price_data = []

        for product in self._products:
            product_price_data.append(
                {
                    "value": uniform(0.50, 10.00),
                    "discount": uniform(0.0, 1.0),
                    "start_date": self.faker.date_this_decade(),
                    "end_date": self.faker.date_this_decade(),
                    "min_quantity": randint(10, 20),
                    "product_id": product["id"],
                }
            )

        self.__write_data(
            csv_file_path=csv_file_path,
            data=product_price_data,
        )

        self._product_prices_data = product_price_data

    def __product_images(self, csv_file_path: str) -> None:
        product_images_data = []

        for product in self._products:
            for i in range(randint(1, 10)):
                product_images_data.append(
                    {
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

        self.__write_data(
            csv_file_path=csv_file_path,
            data=product_images_data,
        )

    def __product_tags(self, csv_file_path: str) -> None:
        product_tags_data = []

        for product in self._products:
            for _ in range(randint(1, 10)):
                product_tags_data.append(
                    {
                        "product_id": product["id"],
                        "tag_id": choice(self.tags).id,
                    }
                )

        self.__write_data(
            csv_file_path=csv_file_path,
            data=product_tags_data,
        )

    def __property_values_to_products(self, csv_file_path: str) -> None:
        property_values_to_products_data = []

        property_values_to_products_count = randint(5, 10)
        property_values_gen = self.__entities_generator(
            entities=self.category_properties,
            count=property_values_to_products_count,
        )

        for product in self._products:
            for property_value in property_values_gen:
                property_values_to_products_data.append(
                    {
                        "product_id": product["id"],
                        "property_value_id": property_value.id,
                        "optional_value": f"{randint(10, 50)}%"
                        if property_value.type.has_optional_value
                        else None,
                    }
                )
                print(property_values_to_products_data)

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
                            "image_url": image,
                            "thumbnail_url": image,
                            "variation_value_to_product_id": product_variation_values_id_auto_increment,
                        }
                    )

                multiplier = uniform(0.1, 2.0)
                product_price = self._product_prices_data[product["id"] - 1]["value"]

                product_variation_prices_data.append(
                    {
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
