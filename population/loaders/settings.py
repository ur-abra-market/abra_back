from core.settings import BaseSettings


class AdminSettings(BaseSettings):
    ADMIN_PASSWORD: str = "Password1Q!"


class UsersSettings(BaseSettings):
    SUPPLIER_EMAIL_LOCAL: str = "supplier"
    SELLER_EMAIL_LOCAL: str = "seller"
    EMAIL_DOMAIN: str = "gmail.com"
    DEFAULT_PASSWORD: str = "Password1!"


admin_settings = AdminSettings()
user_settings = UsersSettings()
