from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .user import User


class Admin(ORMSchema):
    user: Optional[User] = None
