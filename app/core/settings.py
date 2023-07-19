from __future__ import annotations

import json
from os import path
from typing import Any, List, Optional, cast

from pydantic import BaseConfig
from pydantic import BaseSettings as PydanticBaseSettings
from pydantic import Field


class BaseSettings(PydanticBaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class ApplicationSettings(BaseSettings):
    ENV: str = "local"
    COMMIT: str = "local"
    APPLICATION_URL: str
    BACKEND_PORT: int

    @property
    def confirm_registration(self) -> str:
        return path.join(self.APPLICATION_URL, "register/confirm_email")

    @property
    def restore_password(self) -> str:
        return path.join(self.APPLICATION_URL, "reset_password")

    @property
    def change_password(self) -> str:
        return path.join(self.APPLICATION_URL, "change_password")


application_settings = ApplicationSettings()


class LoggingSettings(BaseSettings):
    LOGGING_LEVEL: str


logging_settings = LoggingSettings()


class FastAPIUvicornSettings(BaseSettings):
    DEBUG: bool
    RELOAD: bool
    HOSTNAME: str = "0.0.0.0"
    PORT: int = 80
    DOCS_URL: str
    REDOC_URL: str
    OPENAPI_URL: str


fastapi_uvicorn_settings = FastAPIUvicornSettings()


class DatabaseSettings(BaseSettings):
    DATABASE_DRIVER: str
    DATABASE_USERNAME: str
    DATABASE_PASSWORD: str
    DATABASE_HOSTNAME: str
    DATABASE_PORT: str
    DATABASE_NAME: str

    @property
    def url(self) -> str:
        driver, user, password, host, port, name = (
            self.DATABASE_DRIVER,
            self.DATABASE_USERNAME,
            self.DATABASE_PASSWORD,
            self.DATABASE_HOSTNAME,
            self.DATABASE_PORT,
            self.DATABASE_NAME,
        )

        return f"{driver}://{user}:{password}@{host}:{port}/{name}"


database_settings = DatabaseSettings()


class JWTSettings(BaseSettings):
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRATION_TIME: int
    REFRESH_TOKEN_EXPIRATION_TIME: int
    COOKIE_SECURE: bool
    COOKIE_CSRF: bool
    COOKIE_SAMESITE: str
    COOKIE_DOMAIN: Optional[str] = None
    JWT_SECRET_KEY: str


jwt_settings = JWTSettings()


class CORSSettings(BaseSettings):
    ALLOW_ORIGINS: List[str] = Field(default_factory=list)
    ALLOW_CREDENTIALS: bool
    ALLOW_METHODS: List[str] = Field(default_factory=list)
    ALLOW_HEADERS: List[str] = Field(default_factory=list)

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
    AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET: str
    AWS_S3_IMAGE_USER_LOGO_BUCKET: str
    AWS_S3_COMPANY_IMAGES_BUCKET: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_DEFAULT_REGION: str


aws_s3_settings = AWSS3Settings()


class MailSettings(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool


mail_settings = MailSettings()


class UserSettings(BaseSettings):
    USER_LOGO_THUMBNAIL_X: int
    USER_LOGO_THUMBNAIL_Y: int


user_settings = UserSettings()


class GoogleSettings(BaseSettings):
    CLIENT_ID: Optional[str] = None
    GOOGLE_OAUTH_URL: str = "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token="


google_settings = GoogleSettings()
