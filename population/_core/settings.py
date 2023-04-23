from core.settings import BaseSettings


class AdminSettings(BaseSettings):
    ADMIN_PASSWORD: str = "Password1Q!"


admin_settings = AdminSettings()
