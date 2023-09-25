from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .bundle_product_variation_value import BundleProductVariationValueModel
    from .bundle_variation_pod_amount import BundleVariationPodAmountModel
    from .bundle_variation_pod_price import BundleVariationPodPriceModel
    from .product import ProductModel


class BundleVariationPodModel(mixins.ProductIDMixin, ORMModel):
    bundle_variations: Mapped[List[BundleProductVariationValueModel]] = relationship(
        back_populates="pod"
    )
    bundle_variation_pod_amount: Mapped[Optional[BundleVariationPodAmountModel]] = relationship(
        back_populates="bundle_variation_pod"
    )
    product: Mapped[Optional[ProductModel]] = relationship(back_populates="bundle_variation_pods")
    prices: Mapped[Optional[List[BundleVariationPodPriceModel]]] = relationship(
        back_populates="bundle_variation_pod"
    )
