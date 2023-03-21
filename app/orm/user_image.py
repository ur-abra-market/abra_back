from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, text


class UserImageModel(mixins.UserIDMixin, ORMModel):
    thumbnail_url: Mapped[Optional[text]]
    source_url: Mapped[Optional[text]]
