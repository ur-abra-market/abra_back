from __future__ import annotations

import uuid

from sqlalchemy.orm import Mapped, mapped_column

from .core import ORMModel, mixins, types


class ResetTokenModel(mixins.EmailMixin, mixins.UserIDMixin, ORMModel):
    reset_code: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4)
    status: Mapped[types.bool_no_value]
