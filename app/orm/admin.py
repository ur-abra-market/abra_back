from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .user import UserModel


class AdminModel(mixins.UserIDMixin, ORMModel):
    user: Mapped[Optional[UserModel]] = relationship(back_populates="admin")
