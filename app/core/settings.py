# mypy: disable-error-code="call-arg"

from __future__ import annotations

import json
from os import path
from typing import Any, List, Tuple, cast

from pydantic import BaseConfig
from pydantic import BaseSettings as PydanticBaseSettings
from pydantic import Field


class BaseSettings(PydanticBaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ApplicationSettings(BaseSettings):
    APP_URL: str = "http://localhost:8080"

    @property
    def forgot_password(self):
        reset_code: None = None
        return path.join(self.APP_URL, "register/resetPassword", f"?token={reset_code}")

    @property
    def confirm_registration(self) -> str:
        return path.join(self.APP_URL, "register/email-confirmation")

    @property
    def restore_password(self) -> str:
        return path.join(self.APP_URL, "resetPassword")

    @property
    def change_password(self) -> str:
        return path.join(self.APP_URL, "changePassword")


application_settings = ApplicationSettings()


class DatabaseSettings(BaseSettings):
    RDS_DRIVER: str = "postgresql+asyncpg"
    RDS_USERNAME: str = "postgres"
    RDS_PASSWORD: str = "postgres"
    RDS_HOSTNAME: str = "database"
    RDS_PORT: str = "5432"
    RDS_DB_NAME: str = "postgres"

    @property
    def url(self) -> str:
        driver, user, password, host, port, name = (
            self.RDS_DRIVER,
            self.RDS_USERNAME,
            self.RDS_PASSWORD,
            self.RDS_HOSTNAME,
            self.RDS_PORT,
            self.RDS_DB_NAME,
        )
        return f"{driver}://{user}:{password}@{host}:{port}/{name}"


database_settings = DatabaseSettings()


class FastAPISettings(BaseSettings):
    DEBUG: bool = True


fastapi_settings = FastAPISettings()


class LoggingSettings(BaseSettings):
    LOGGING_LEVEL: str = "DEBUG"
    LOGGING_FILE_PATH: str = "logs/app.log"
    CUSTOM_LOGGING_ON: bool = False


logging_settings = LoggingSettings()


class UvicornSettings(BaseSettings):
    HOSTNAME: str = "0.0.0.0"
    PORT: int = 8080
    RELOAD: bool = False


uvicorn_settings = UvicornSettings()


class SwaggerSettings(BaseSettings):
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"


swagger_settings = SwaggerSettings()


class JWTSettings(BaseSettings):
    ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRATION_TIME: int = 60 * 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRATION_TIME: int = 60 * 60 * 24 * 14  # 14 days
    COOKIE_SECURE: bool = not fastapi_settings.DEBUG
    COOKIE_SAMESITE: str = "lax"
    COOKIE_DOMAIN: str


jwt_settings = JWTSettings()


class CORSSettings(BaseSettings):
    ALLOW_ORIGINS: List[str] = Field(default_factory=list)

    class Config(BaseConfig):
        @staticmethod
        def list_parse(v: Any) -> List[str]:
            try:
                return cast(List[str], json.loads(v))
            except Exception:
                return list(filter(lambda x: x.strip(), v.split(",")))

        json_loads = list_parse


cors_settings = CORSSettings()


class AWSS3Settings(BaseSettings):
    AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET: str = Field(env="AWS_BUCKET")
    AWS_S3_IMAGE_USER_LOGO_BUCKET: str
    AWS_S3_COMPANY_IMAGES_BUCKET: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str
    AWS_BUCKET: str


aws_s3_settings = AWSS3Settings()


class EmailSettings(BaseSettings):
    MAIL_USERNAME: str = Field(..., env="EMAIL_USERNAME")
    MAIL_PASSWORD: str = Field(..., env="EMAIL_PASS")
    MAIL_FROM: str = Field(..., env="EMAIL_USERNAME")
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Abra market"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True


email_settings = EmailSettings()


class ImageSettings(BaseSettings):
    USER_LOGO_THUMBNAIL_SIZE: Tuple[int, int] = (100, 100)


image_settings = ImageSettings()
