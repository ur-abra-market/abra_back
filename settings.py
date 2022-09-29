from os import getenv


DEBUG = bool(int(getenv("DEBUG", 0)))

# swagger's settings
DOCS_URL = "/docs" if DEBUG else None
REDOC_URL = "/redoc" if DEBUG else None
OPENAPI_URL = "/openapi.json" if DEBUG else None

COOKIE_SECURE = not DEBUG
