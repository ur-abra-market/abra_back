from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .user import User


class Seller(mixins.UserIDMixin, ORMSchema):
    user: Mapped[Optional[User]] = None
