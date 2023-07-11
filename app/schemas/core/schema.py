from __future__ import annotations

from ..schema import ApplicationORMSchema
from .mixins import IDMixin


class ORMSchema(IDMixin, ApplicationORMSchema):
    ...
