from __future__ import annotations

from typing import List, Union

from .abc import MailABC

TEMPLATE = """
<div style="display: flex; align-items: center; justify-content: center; flex-direction: column">
    <h3>Подтверждение электронной почты</h3>
    <br>
    <p>Благодарим вас за регистрацию на нашей платформе, ниже ссылка для подтвержения электронной почты:</p>
    <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; "
       href="{host}/register/confirmEmail/?token={token}">Подтвердить</a>
    <p>Если вы не регистрировались на abra-market.com, пожалуйста игнорируйте данное сообщение!</p>
</div>
"""


class MailConfirm(MailABC):
    TEMPLATE = TEMPLATE

    def _format_template(self, host: str, token: str) -> str:
        return self.TEMPLATE.format(host=host, token=token)

    async def _send(
        self, subject: str, recipients: Union[str, List[str]], host: str, token: str
    ) -> None:
        await self.interface.send_mail(
            subject=subject,
            recipients=recipients,
            body=self._format_template(host=host, token=token),
        )
