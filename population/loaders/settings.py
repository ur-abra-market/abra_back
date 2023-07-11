from __future__ import annotations

from core.settings import BaseSettings


class AdminSettings(BaseSettings):
    ADMIN_PASSWORD: str = "Password1Q!"


class UsersSettings(BaseSettings):
    SUPPLIER_EMAIL: str = "supplier@mail.ru"
    SELLER_EMAIL: str = "seller@mail.ru"
    DEFAULT_PASSWORD: str = "Password1!"


admin_settings = AdminSettings()
user_settings = UsersSettings()
