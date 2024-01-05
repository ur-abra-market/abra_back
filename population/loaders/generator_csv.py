from __future__ import annotations

import abc
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

from .settings import population_settings


@dataclass(slots=True)
class CsvGenerator:
    categories: list[CategoryModel]
    suppliers: list[SupplierModel]
    brands: list[BrandModel]
    category_properties: list[PropertyValueModel]
    category_variation_types: list[VariationTypeModel]
    category_variation_type_ids: list[int]
    category_variation_values: list[VariationValueModel]

    products: list[dict[str, Any]]
    product_prices: list[dict[str, Any]]
    product_images: list[dict[str, Any]]

    faker: Faker = Faker()

    def generate_csv_content(self) -> None:
        self._products(
            csv_file_path="",
            suppliers=self.suppliers,
            categories=self.categories,
            brands=self.brands,
        )
        self._product_prices(
            csv_file_path="",
            products=self.products,
        )

    def _get_image_url(self, width: int, height: int) -> str:
        urls = [
            "https://place.dog/{width}/{height}".format(width=width, height=height),
            "https://picsum.photos/id/{image}/{width}/{height}".format(
                width=width, height=height, image=randint(1, 500)
            ),
        ]
        return choice(urls)

    def _get_squared_image_thumbnail_urls(self, sizes: list[tuple[int, int]]) -> dict[str, Any]:
        return {f"thumbnail_{size[0]}": self._get_image_url(*size) for size in sizes}

    def _products(
        self,
        csv_file_path: str,
        suppliers: list[SupplierModel],
        categories: list[SupplierModel],
        brands: list[BrandModel],
    ) -> None:
        product_data = []

        for supplier in suppliers:
            for category in categories:
                if supplier.id == 1 and category.id == 3:
                    continue
                product_count = randint(0, population_settings.PRODUCTS_COUNT_RANGE)
                for i in range(product_count):
                    create_update_datetime = self.faker.date_this_decade()
                    product_data.append(
                        {
                            "id": i + 1,
                            "name": self.faker.sentence(nb_words=randint(1, 4)).strip("."),
                            "description": self.faker.sentence(nb_words=10),
                            "supplier_id": supplier.id,
                            "category_id": category.id,
                            "grade_average": uniform(0.0, 5.0),
                            "is_active": True,
                            "brand_id": choice(brands).id,
                            "created_at": create_update_datetime,
                            "updated_at": create_update_datetime,
                        }
                    )

                fields = product_data[0].keys()

                with open(csv_file_path, "r", newline="") as products_csv:
                    writer = DictWriter(products_csv, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(product_data)

                self.products = product_data

    def _product_prices(self, csv_file_path: str, products: list[dict[str, Any]]) -> None:
        product_price_data = []

        for product in products:
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

        fields = product_price_data[0].keys()

        with open(csv_file_path, "r", newline="") as product_prices_csv:
            writer = DictWriter(product_prices_csv, fieldnames=fields)
            writer.writeheader()
            writer.writerows(product_price_data)

            self.product_prices = product_price_data

    def _product_images(self, csv_file_path: str, products: list[dict[str, Any]]) -> None:
        product_images_data = []

        for product in products:
            for i in range(randint(1, 10)):
                product_images_data.append(
                    {
                        "product_id": product["id"],
                        "image_url": self.faker.image_url(
                            placeholder_url=self._get_image_url(width=900, height=900)
                        ),
                        "thumbnail_urls": self._get_squared_image_thumbnail_urls(
                            sizes=upload_file_settings.PRODUCT_THUMBNAIL_PROPERTIES
                        ),
                        "order": i,
                    }
                )

        fields = product_images_data[0].keys()

        with open(csv_file_path, "r", newline="") as product_prices_csv:
            writer = DictWriter(product_prices_csv, fieldnames=fields)
            writer.writeheader()
            writer.writerows(product_images_data)

            self.product_images = product_images_data
