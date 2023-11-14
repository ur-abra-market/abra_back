from __future__ import annotations

from uuid import UUID

from schemas.schema import ApplicationSchema


class TokenConfirmationUpload(ApplicationSchema):
    token: UUID
