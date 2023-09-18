from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .bundle_variation import BundleVariationModel
    from .bundle_variation_pod_amount import BundleVariationPodAmountModel
    from .product import ProductModel
    from .bundle_pod_price import BundlePodPriceModel


class BundleVariationPodModel(mixins.ProductIDMixin, ORMModel):
    bundle_variations: Mapped[List[BundleVariationModel]] = relationship(back_populates="pod")
    bundle_variation_pod_amount: Mapped[Optional[BundleVariationPodAmountModel]] = relationship(back_populates="bundle_variation_pod")
    product: Mapped[Optional[ProductModel]] = relationship(back_populates="bundle_variation_pods")
    prices: Mapped[Optional[List[BundlePodPriceModel]]] = relationship(back_populates="bundle_variation_pod")