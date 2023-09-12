from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import bundle_variation_pod_id_fk
from ..types import bundle_variation_pod_id_fk_type


class BundleVariationPodIDMixin:
    bundle_variation_pod_id: Mapped[bundle_variation_pod_id_fk_type] = bundle_variation_pod_id_fk
