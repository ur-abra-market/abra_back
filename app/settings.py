from os import getenv


DEBUG = bool(int(getenv("DEBUG", 0)))


# Auto-reloading
RELOAD = bool(int(getenv("RELOAD", 0)))

# swagger's settings
DOCS_URL = "/docs" if DEBUG else None
REDOC_URL = "/redoc" if DEBUG else None
OPENAPI_URL = "/openapi.json" if DEBUG else None

ALLOW_ORIGINS = [
    item for item in getenv("ALLOW_ORIGINS", "").split(",") if item.strip()
]

# jwt auth settings
COOKIE_SECURE = not DEBUG
# COOKIE_SAMESITE = "none" if DEBUG else "lax"
COOKIE_SAMESITE = "lax"
IS_CSRF_TOKEN_ENABLED = bool(int(getenv("IS_CSRF_TOKEN_ENABLED", 1)))

COOKIE_DOMAIN = getenv("COOKIE_DOMAIN")

AWS_S3_SUPPLIERS_PRODUCT_UPLOAD_IMAGE_BUCKET = getenv("AWS_BUCKET")
AWS_S3_IMAGE_USER_LOGO_BUCKET = getenv("AWS_S3_IMAGE_USER_LOGO_BUCKET")
AWS_S3_COMPANY_IMAGES_BUCKET = getenv("AWS_S3_COMPANY_IMAGES_BUCKET")

# image settings
USER_LOGO_THUMBNAIL_SIZE = (100, 100)
