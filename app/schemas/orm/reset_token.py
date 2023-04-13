from __future__ import annotations

from pydantic import UUID4

from .core import ORMSchema, mixins


class ResetToken(mixins.EmailMixin, ORMSchema):
    reset_code: UUID4
    status: bool
