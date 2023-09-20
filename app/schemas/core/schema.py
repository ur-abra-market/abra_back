from __future__ import annotations

from ..schema import ApplicationORMSchema
from .mixins import IDMixin, TimestampMixin


class ORMSchema(TimestampMixin, IDMixin, ApplicationORMSchema):
    ...
