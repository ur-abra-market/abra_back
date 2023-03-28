from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, order_product_variation_fk, text


class OrderNoteModel(ORMModel):
    text: Mapped[text]

    order_product_variation_id: Mapped[order_product_variation_fk]
