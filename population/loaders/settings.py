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
