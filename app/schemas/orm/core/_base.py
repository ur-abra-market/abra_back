from __future__ import annotations

from ...schema import ApplicationORMSchema
from . import mixins


class ORMSchema(mixins.IDMixin, ApplicationORMSchema):
    ...
