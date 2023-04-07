from __future__ import annotations

from typing import List, Union

from .abc import MailABC

TEMPLATE = """
<div style="width:100%;font-family: monospace;">
    <h1>Привет!</h1>
    <p>Кто-то создал запрос на сброс и смену пароля. Если это были вы, вы можете сбросить\
    и сменить свой пароль, перейдя по ссылке ниже:</p>
    <a style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem; text-decoration: none; " href="{host}/password/reset/?token={token}">Подтвердить</a>
    <p>Если это были не вы, пожалуйста, игнорируйте данное письмо!</p>
    <p>Ваш пароль не поменяется, если вы не перейдете по ссылке.</p>
</div>
"""


class MailForgot(MailABC):
    TEMPLATE = TEMPLATE

    def _format_template(self, host: str, reset_code: str) -> str:
        return self.TEMPLATE.format(host=host, token=reset_code)

    async def _send(
        self, subject: str, recipients: Union[str, List[str]], host: str, reset_code: str
    ) -> None:
        await self.interface.send_mail(
            subject=subject,
            recipients=recipients,
            body=self._format_template(host=host, reset_code=reset_code),
        )
