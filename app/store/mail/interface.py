from __future__ import annotations

from typing import List, Union

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from core.settings import email_settings

SUBTYPE = "html"


class MailInterface:
    connection_config = ConnectionConfig(
        MAIL_USERNAME=email_settings.MAIL_USERNAME,
        MAIL_PASSWORD=email_settings.MAIL_PASSWORD,
        MAIL_FROM=email_settings.MAIL_FROM,
        MAIL_PORT=email_settings.MAIL_PORT,
        MAIL_SERVER=email_settings.MAIL_SERVER,
        MAIL_FROM_NAME=email_settings.MAIL_FROM_NAME,
        MAIL_STARTTLS=email_settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=email_settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=email_settings.USE_CREDENTIALS,
    )

    def __init__(self, subtype: str = SUBTYPE) -> None:
        self.fast_mail = FastMail(self.connection_config)
        self.subtype = subtype

    async def send_mail(self, subject: str, recipients: Union[str, List[str]], body: str) -> None:
        if not isinstance(recipients, List):
            recipients = [recipients]

        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype=SUBTYPE,
        )
        await self.fast_mail.send_message(message)
