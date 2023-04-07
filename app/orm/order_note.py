from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, order_product_variation_fk
from .core import text as t


class OrderNoteModel(ORMModel):
    text: Mapped[t]

    order_product_variation_id: Mapped[order_product_variation_fk]
