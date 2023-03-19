from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core.types import company_id_fk


class CompanyIDMixin:
    company_id: Mapped[company_id_fk]
