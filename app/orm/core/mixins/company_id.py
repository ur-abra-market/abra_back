from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import company_id_fk
from ..types import company_id_fk_type


class CompanyIDMixin:
    company_id: Mapped[company_id_fk_type] = company_id_fk
