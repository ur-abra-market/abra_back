from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped

from app.orm.core import ORMModel, mixins


class UserImageModel(mixins.UserIDMixin, ORMModel):
    thumbnail_url: Mapped[Optional[str]]
    source_url: Mapped[Optional[str]]
