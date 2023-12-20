from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .variation_type import VariationType


class VariationValue(ORMSchema):
    value: str
    variation_type_id: int
    image_url: Optional[str]

    type: Optional[VariationType] = None
    variation: Optional[int] = None
