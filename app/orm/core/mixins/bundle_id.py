from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import bundle_id_fk
from ..types import bundle_id_fk_type


class BundleIDMixin:
    bundle_id: Mapped[bundle_id_fk_type] = bundle_id_fk
