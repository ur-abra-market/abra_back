from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .brand import Brand
    from .bundle import Bundle
    from .bundle_variation_pod import BundleVariationPod
    from .category import Category
    from .product_image import ProductImage
    from .product_price import ProductPrice
    from .product_review import ProductReview
    from .property_type import ProductPropertyType
    from .seller import Seller
    from .supplier import Supplier
    from .tags import Tags
    from .variation_value_to_product import VariationValueToProduct


class Product(ORMSchema):
    name: str
    description: Optional[str] = None
    grade_average: float = 0.0
    total_orders: int = 0
    reviews_count: Optional[int] = 0
    is_active: bool = True

    is_favorite: Optional[bool] = None

    prices: Optional[List[ProductPrice]] = None
    min_price: float = 0
    max_price: float = 0
    brand: Optional[Brand] = None
    category: Optional[Category] = None
    supplier: Optional[Supplier] = None
    images: Optional[List[ProductImage]] = None
    tags: Optional[List[Tags]] = None
    property_types: Optional[List[ProductPropertyType]] = None
    product_variations: Optional[List[VariationValueToProduct]] = None
    favorites_by_users: Optional[List[Seller]] = None
    reviews: Optional[List[ProductReview]] = None
    bundles: Optional[List[Bundle]] = None
    bundle_variation_pods: Optional[List[BundleVariationPod]] = None

    up_to_discount: Optional[float] = None
    breadcrumbs: Optional[List[Category]] = None
