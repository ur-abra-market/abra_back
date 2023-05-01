from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .seller import Seller


class SellerImage(ORMSchema):
    source_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    seller: Optional[Seller] = None
