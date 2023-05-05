from pathlib import Path

from fastapi_mail import ConnectionConfig

from core.settings import mail_settings

TEMPLATE_FOLDER = Path(__file__).parent / "templates"
CONNECTION_CONFIG = ConnectionConfig(
    EMAIL_USERNAME=mail_settings.EMAIL_USERNAME,
    EMAIL_PASSWORD=mail_settings.EMAIL_PASSWORD,
    EMAIL_FROM=mail_settings.EMAIL_FROM,
    EMAIL_PORT=mail_settings.EMAIL_PORT,
    EMAIL_SERVER=mail_settings.EMAIL_SERVER,
    EMAIL_FROM_NAME=mail_settings.EMAIL_FROM_NAME,
    EMAIL_STARTTLS=mail_settings.EMAIL_STARTTLS,
    EMAIL_SSL_TLS=mail_settings.EMAIL_SSL_TLS,
    USE_CREDENTIALS=mail_settings.USE_CREDENTIALS,
    TEMPLATE_FOLDER=TEMPLATE_FOLDER,
)
