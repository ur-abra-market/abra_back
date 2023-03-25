from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, text

if TYPE_CHECKING:
    from .user import UserModel


class UserCredentialsModel(mixins.UserIDMixin, ORMModel):
    password: Mapped[text]

    user: Mapped[Optional[UserModel]] = relationship(back_populates="credentials")
