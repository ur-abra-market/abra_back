from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped

from ..constraints import tag_id_fk
from ..types import tag_id_fk_type


class TagIDMixin:
    tag_id: Mapped[Optional[tag_id_fk_type]] = tag_id_fk
