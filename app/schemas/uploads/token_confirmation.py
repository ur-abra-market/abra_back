from __future__ import annotations

from ..schema import ApplicationSchema


class TokenConfirmationUpload(ApplicationSchema):
    token: str
