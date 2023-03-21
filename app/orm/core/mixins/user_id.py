from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..types import user_id_fk


class UserIDMixin:
    user_id: Mapped[user_id_fk]
