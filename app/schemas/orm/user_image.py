from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .user import User


class UserImage(mixins.UserIDMixin, ORMSchema):
    source_url: str
    thumbnail_url: Optional[str] = None
    user: Optional[User] = None
