from os import getenv


DEBUG = bool(int(getenv("DEBUG", 0)))

# swagger's settings
DOCS_URL = "/docs" if DEBUG else None
REDOC_URL = "/redoc" if DEBUG else None
OPENAPI_URL = "/openapi.json" if DEBUG else None

ALLOW_ORIGINS = [item for item in getenv("ALLOW_ORIGINS").split(',') if item.strip()]

# jwt auth settings
COOKIE_SECURE = not DEBUG
# COOKIE_SAMESITE = "none" if DEBUG else "lax"
COOKIE_SAMESITE = "lax"

COOKIE_DOMAIN = getenv("COOKIE_DOMAIN")
