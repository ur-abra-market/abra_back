from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .bundle_variation import BundleVariation


class BundleVariationPod(ORMSchema):
    bundle_variation: Optional[List[BundleVariation]] = None
