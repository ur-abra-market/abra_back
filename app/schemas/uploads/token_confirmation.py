from __future__ import annotations

from schemas.schema import ApplicationSchema


class TokenConfirmationUpload(ApplicationSchema):
    token: str
