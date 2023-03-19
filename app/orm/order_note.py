from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core import ORMModel, order_product_variation_fk


class OrderNoteModel(ORMModel):
    text: Mapped[str]

    order_product_variation_id: Mapped[order_product_variation_fk]
