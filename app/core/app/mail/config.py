from pathlib import Path

from fastapi_mail import ConnectionConfig

from core.settings import mail_settings

TEMPLATE_FOLDER = Path(__file__).parent / "templates"
CONNECTION_CONFIG = ConnectionConfig(
    MAIL_USERNAME=mail_settings.USERNAME,
    MAIL_PASSWORD=mail_settings.PASSWORD,
    MAIL_FROM=mail_settings.FROM,
    MAIL_PORT=mail_settings.PORT,
    MAIL_SERVER=mail_settings.SERVER,
    MAIL_FROM_NAME=mail_settings.FROM_NAME,
    MAIL_STARTTLS=mail_settings.STARTTLS,
    MAIL_SSL_TLS=mail_settings.SSL_TLS,
    USE_CREDENTIALS=mail_settings.USE_CREDENTIALS,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER,
)
