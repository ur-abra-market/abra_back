from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core import ORMModel, mixins, str_50


class ResetTokenModel(mixins.EmailMixin, mixins.UserIDMixin, ORMModel):
    reset_code: Mapped[str_50]
    status: Mapped[bool]
