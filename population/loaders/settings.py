from __future__ import annotations

from core.settings import BaseSettings


class AdminSettings(BaseSettings):
    ADMIN_PASSWORD: str = "Password1Q!"


class PopulationSettings(BaseSettings):
    SUPPLIER_EMAIL_LOCAL: str = "supplier"
    SELLER_EMAIL_LOCAL: str = "seller"
    EMAIL_DOMAIN: str = "gmail.com"
    DEFAULT_PASSWORD: str = "Password1!"
    SUPPLIERS_COUNT: int = 2
    SELLERS_COUNT: int = 2
    PRODUCTS_COUNT_RANGE: int = 20


admin_settings = AdminSettings()
population_settings = PopulationSettings()
