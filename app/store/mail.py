from typing import Optional, Union, List

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from core.settings import email_settings


SUBTYPE = "html"

BODY = """
<div style="width:100%;font-family: monospace;">
    <h1>Привет</h1>
    <p>Кто-то создал запрос на сброс и смену пароля. Если это были вы, вы можете сбросить\
        и сменить свой пароль, перейдя по ссылке ниже:</p>
    <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; "
       href="{host}/password/resetPassword/?token={token}">Подтвердить</a>
    <p>Если это были не вы, пожалуйста, игнорируйте данное письмо!</p>
    <p>Ваш пароль не поменяется, если вы не перейдете по ссылке.</p>
</div>
"""

CONFIRMATION_BODY = """
<div style="display: flex; align-items: center; justify-content: center; flex-direction: column">
    <h3>Подтверждение электронной почты</h3>
    <br>
    <p>Благодарим вас за регистрацию на нашей платформе, ниже ссылка для подтвержения электронной почты:</p>
    <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; "
       href="{host}/register/confirmEmail/?token={token}">Подтвердить</a>
    <p>Если вы не регистрировались на abra-market.com, пожалуйста игнорируйте данное сообщение!</p>
</div>
"""


class Mail:
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

    def __init__(self, connection_config: Optional[ConnectionConfig] = None) -> None:
        self.fast_mail = (
            FastMail(self.connection_config)
            if connection_config is None
            else FastMail(connection_config)
        )

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

    def format_confirmation_body(self, host: str, token: str) -> str:
        return CONFIRMATION_BODY.format(host=host, token=token)

    async def send_confirmation_mail(
        self, subject: str, recipients: Union[str, List[str]], host: str, token: str
    ) -> None:
        await self.send_mail(
            subject=subject,
            recipients=recipients,
            body=self.format_confirmation_body(host=host, token=token),
        )

    def format_body(self, host: str, token: str) -> str:
        return BODY.format(host=host, token=token)

    async def send_forgot_password_mail(
        self, subject: str, recipients: Union[str, List[str]], host: str, token: str
    ) -> None:
        await self.send_mail(
            subject=subject,
            recipients=recipients,
            body=self.format_confirmation_body(host=host, token=token),
        )
