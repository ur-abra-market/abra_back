from __future__ import annotations

import json
from typing import List, Tuple, Optional, Dict, Any

from pydantic import BaseConfig, BaseSettings, Field


class AppBaseSettings(BaseSettings):
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class DatabaseSettings(AppBaseSettings):
    RDS_DRIVER: str = "mysql+aiomysql"
    RDS_USERNAME: str = ""
    RDS_PASSWORD: str = ""
    RDS_HOSTNAME: str = ""
    RDS_PORT: str = ""
    RDS_DB_NAME: str = ""

    @property
    def url(self) -> str:
        return "{driver}://{user}:{password}@{host}:{port}/{name}".format(
            driver=self.RDS_DRIVER,
            user=self.RDS_USERNAME,
            password=self.RDS_PASSWORD,
            host=self.RDS_HOSTNAME,
            port=self.RDS_PORT,
            name=self.RDS_DB_NAME,
        )


database_settings = DatabaseSettings()


class FastAPISettings(BaseSettings):
    DEBUG: bool = False


fastapi_settings = FastAPISettings()


class LoggingSettings(AppBaseSettings):
    LOGGING_LEVEL: str = "DEBUG"
    LOGGING_FILE_PATH: str = "app/logs/app.log"
    CUSTOM_LOGGING_ON: bool = False


logging_settings = LoggingSettings()


class UvicornSettings(BaseSettings):
    HOSTNAME: str = "0.0.0.0"
    PORT: int = 8080
    RELOAD: bool = False
    RELOAD_EXCLUDE_FILES = ["*.log"]


uvicorn_settings = UvicornSettings()


class SwaggerSettings(BaseSettings):
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"


swagger_settings = SwaggerSettings()


class JWTSettings(BaseSettings):
    JWT_SECRET_KEY: str = "1"
    COOKIE_SECURE: bool = not fastapi_settings.DEBUG
    COOKIE_SAMESITE: str = "lax"
    IS_CSRF_TOKEN_ENABLED: bool = True
    COOKIE_DOMAIN: str = "localhost"


jwt_settings = JWTSettings()


class CORSSettings(BaseSettings):
    ALLOW_ORIGINS: List[str] = Field(default_factory=list)

    class Config(BaseConfig):
        @staticmethod
        def list_parse(v) -> List[str]:
            try:
                return json.loads(v)
            except Exception:
                return list(filter(lambda x: x.strip(), v.split(",")))

        json_loads = list_parse


cors_settings = CORSSettings()


class AWSS3Settings(BaseSettings):
    AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET: str = Field("", env="AWS_BUCKET")
    AWS_S3_IMAGE_USER_LOGO_BUCKET: str = ""
    AWS_S3_COMPANY_IMAGES_BUCKET: str = ""


aws_s3_settings = AWSS3Settings()


class ImageSettings(BaseSettings):
    USER_LOGO_THUMBNAIL_SIZE: Tuple[int, int] = (100, 100)


image_settings = ImageSettings()