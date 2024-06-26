from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .admin import Admin
    from .country import Country
    from .seller import Seller
    from .supplier import Supplier


class User(
    mixins.EmailMixin, mixins.NameMixin, mixins.PhoneMixin, mixins.TimestampMixin, ORMSchema
):
    is_verified: bool = False
    is_deleted: bool = False
    is_supplier: bool = False
    admin: Optional[Admin] = None
    seller: Optional[Seller] = None
    supplier: Optional[Supplier] = None
    country: Optional[Country] = None
