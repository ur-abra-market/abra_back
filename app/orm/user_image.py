from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, text

if TYPE_CHECKING:
    from .user import UserModel


class UserImageModel(mixins.UserIDMixin, ORMModel):
    source_url: Mapped[text]
    thumbnail_url: Mapped[Optional[text]]

    user: Mapped[Optional[UserModel]] = relationship(back_populates="image")
