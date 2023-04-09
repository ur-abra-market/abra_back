from __future__ import annotations

from typing import Optional

from .core import ORMSchema, mixins


class CompanyImage(mixins.CompanyIDMixin, ORMSchema):
    url: Optional[str] = None
    order: int
