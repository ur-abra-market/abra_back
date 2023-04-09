from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .user import User


class Seller(mixins.UserIDMixin, ORMSchema):
    user: Optional[User] = None
