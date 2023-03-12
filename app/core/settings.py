import json
from typing import List, Tuple

from pydantic import BaseConfig, BaseSettings, Field


class FastAPISettings(BaseSettings):
    DEBUG: bool = False


fastapi_settings = FastAPISettings()


class UvicornSettings(BaseSettings):
    RELOAD: bool = False


uvicorn_settings = UvicornSettings()


class SwaggerSettings(BaseSettings):
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    OPENAPI_URL: str = "/openapi.json"


swagger_settings = SwaggerSettings()


class JWTSettings(BaseSettings):
    COOKIE_SECURE: bool = not fastapi_settings.DEBUG
    COOKIE_SAMESITE: str = "lax"
    IS_CSRF_TOKEN_ENABLED: bool = True
    COOKIE_DOMAIN: str


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
    AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET: str
    AWS_S3_IMAGE_USER_LOGO_BUCKET: str
    AWS_S3_COMPANY_IMAGES_BUCKET: str


aws_s3_settings = AWSS3Settings()


class ImageSettings(BaseSettings):
    USER_LOGO_THUMBNAIL_SIZE: Tuple[int, int] = (100, 100)


image_settings = ImageSettings()
