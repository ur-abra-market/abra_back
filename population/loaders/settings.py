from __future__ import annotations

from core.settings import BaseSettings


class AdminSettings(BaseSettings):
    PASSWORD: str = "Password1Q!"

    class Config:
        env_prefix: str = "ADMIN_"


class PopulationSettings(BaseSettings):
    SUPPLIER_EMAIL_LOCAL: str = "supplier"
    SELLER_EMAIL_LOCAL: str = "seller"
    EMAIL_DOMAIN: str = "gmail.com"
    DEFAULT_PASSWORD: str = "Password1!"
    SUPPLIERS_COUNT: int = 2
    SELLERS_COUNT: int = 2
    PRODUCTS_COUNT_RANGE: int = 20
    REVIEWS_PER_SELLER_RANGE: int = 100
    PHOTOS_PER_REVIEW_LIMIT: int = 5

    class Config:
        env_prefix: str = "POPULATION_"


admin_settings = AdminSettings()
population_settings = PopulationSettings()


# CSV PATH CONSTANTS

PRODUCTS_CSV_PATH = "population/loaders/csv/products.csv"
PRODUCT_PRICES_CSV_PATH = "population/loaders/csv/product_prices.csv"
PRODUCT_IMAGES_CSV_PATH = "population/loaders/csv/product_images.csv"
PRODUCT_TAGS_CSV_PATH = "population/loaders/csv/product_tags.csv"
PROPERTY_VALUES_TO_PRODUCTS_CSV_PATH = "population/loaders/csv/property_values_to_products.csv"
PRODUCT_VARIATION_VALUES_CSV_PATH = "population/loaders/csv/variation_values_to_products.csv"
VARIATION_IMAGES_CSV_PATH = "population/loaders/csv/variation_images.csv"
PRODUCT_VARIATION_PRICES_CSV_PATH = "population/loaders/csv/product_variation_prices.csv"
BUNDLES_CVS_PATH = "population/loaders/csv/bundles.csv"
BUNDLABLE_VARIATION_VALUES_CSV_PATH = "population/loaders/csv/bundlable_variation_values.csv"
BUNDLE_PRICES_CSV_PATH = "population/loaders/csv/bundle_prices.csv"
