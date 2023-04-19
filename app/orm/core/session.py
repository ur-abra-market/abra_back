# mypy: disable-error-code="no-redef"
import traceback

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

root_process = traceback.format_stack()[0]
if "bin/alembic" in root_process:
    from app.core.settings import database_settings, fastapi_settings
else:
    from core.settings import database_settings, fastapi_settings  # noqa


POOL_RECYCLE = 60 * 5  # 300

_engine = create_async_engine(
    database_settings.url,
    pool_recycle=POOL_RECYCLE,
    isolation_level="SERIALIZABLE",
    echo=fastapi_settings.DEBUG,
)
async_sessionmaker = sessionmaker(
    bind=_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
