from __future__ import annotations

from ..schema import ApplicationSchema


class BundlesPriceUpload(ApplicationSchema):
    bundle_id: int
    discount: float
