from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import user_id_fk
from ..types import user_id_fk_type


class UserIDMixin:
    user_id: Mapped[user_id_fk_type] = user_id_fk
