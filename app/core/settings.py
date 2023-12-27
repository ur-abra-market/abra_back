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
    URL: str
    BACKEND_PORT: int

    class Config:
        env_prefix: str = "APP_"

    @property
    def confirm_registration(self) -> str:
        return path.join(self.URL, "register/confirm_email")

    @property
    def restore_password(self) -> str:
        return path.join(self.URL, "reset_password")

    @property
    def change_password(self) -> str:
        return path.join(self.URL, "change_password")


application_settings = ApplicationSettings()


class LoggingSettings(BaseSettings):
    MAIN_LOGGER_NAME: str = "abra"
    LEVEL: str

    class Config:
        env_prefix: str = "LOGGING_"


logging_settings = LoggingSettings()


class FastAPIUvicornSettings(BaseSettings):
    DEBUG: bool
    RELOAD: bool
    HOSTNAME: str = "0.0.0.0"
    PORT: int = 80
    DOCS_URL: str
    REDOC_URL: str
    OPENAPI_URL: str

    class Config:
        env_prefix: str = "FASTAPI_"


fastapi_uvicorn_settings = FastAPIUvicornSettings()


class DatabaseSettings(BaseSettings):
    DRIVER: str
    USERNAME: str
    PASSWORD: str
    HOSTNAME: str
    PORT: str
    NAME: str

    class Config:
        env_prefix: str = "DATABASE_"

    @property
    def url(self) -> str:
        driver, user, password, host, port, name = (
            self.DRIVER,
            self.USERNAME,
            self.PASSWORD,
            self.HOSTNAME,
            self.PORT,
            self.NAME,
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
    SECRET_KEY: str

    class Config:
        env_prefix: str = "JWT_"


jwt_settings = JWTSettings()


class CORSSettings(BaseSettings):
    ALLOW_ORIGINS: List[str] = Field(default_factory=list)
    ALLOW_CREDENTIALS: bool
    ALLOW_METHODS: List[str] = Field(default_factory=list)
    ALLOW_HEADERS: List[str] = Field(default_factory=list)

    class Config(BaseConfig):
        env_prefix: str = "CORS_"

        @staticmethod
        def list_parse(v: Any) -> List[str]:
            try:
                return cast(List[str], json.loads(v))
            except Exception:
                return list(filter(lambda x: x.strip(), v.split(",")))

        json_loads = list_parse


cors_settings = CORSSettings()


class AWSS3Settings(BaseSettings):
    S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET: str
    S3_IMAGE_USER_LOGO_BUCKET: str
    S3_COMPANY_IMAGES_BUCKET: str
    ACCESS_KEY_ID: str
    SECRET_ACCESS_KEY: str
    DEFAULT_REGION: str

    class Config:
        env_prefix: str = "AWS_"


aws_s3_settings = AWSS3Settings()


class MailSettings(BaseSettings):
    USERNAME: str
    PASSWORD: str
    FROM: str
    PORT: int
    SERVER: str
    FROM_NAME: str
    STARTTLS: bool
    SSL_TLS: bool
    USE_CREDENTIALS: bool

    class Config:
        env_prefix: str = "MAIL_"


mail_settings = MailSettings()


class UserSettings(BaseSettings):
    LOGO_THUMBNAIL_X: int
    LOGO_THUMBNAIL_Y: int

    class Config:
        env_prefix: str = "USER_"


user_settings = UserSettings()


class GoogleSettings(BaseSettings):
    CLIENT_ID: Optional[str] = None
    OAUTH_URL: str = "https://www.googleapis.com/oauth2/v2/userinfo"

    class Config:
        env_prefix: str = "GOOGLE_"


google_settings = GoogleSettings()


class UploadFileSettings(BaseSettings):
    IMAGE_SIZE_LIMIT_MB: int = 5
    IMAGE_CONTENT_TYPE_LIMIT: set = {
        "image/jpeg",  # .jpg, .jfif, .jpeg extensions are treated by the same definition
        "image/png",
        "image/webp",
    }
    PRODUCT_THUMBNAIL_PROPERTIES: list[tuple[int, int]] = [
        (48, 48),
        (64, 64),
        (106, 106),
        (120, 120),
        (220, 220),
    ]

    class Config:
        env_prefix: str = "UPLOAD_FILE_"


upload_file_settings = UploadFileSettings()


class TestsSettings(BaseSettings):
    TESTS_RUNNING: Optional[bool] = False


tests_settings = TestsSettings()


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str


redis_settings = RedisSettings()