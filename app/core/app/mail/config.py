from pathlib import Path

from fastapi_mail import ConnectionConfig

from core.settings import email_settings

TEMPLATE_FOLDER = Path(__file__).parent / "templates"
CONNECTION_CONFIG = ConnectionConfig(
    MAIL_USERNAME=email_settings.MAIL_USERNAME,
    MAIL_PASSWORD=email_settings.MAIL_PASSWORD,
    MAIL_FROM=email_settings.MAIL_FROM,
    MAIL_PORT=email_settings.MAIL_PORT,
    MAIL_SERVER=email_settings.MAIL_SERVER,
    MAIL_FROM_NAME=email_settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=email_settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=email_settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=email_settings.USE_CREDENTIALS,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER,
)
