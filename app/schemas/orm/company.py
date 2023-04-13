from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .supplier import Supplier


class Company(mixins.BusinessEmailMixin, mixins.PhoneMixin, ORMSchema):
    name: Optional[str] = None
    is_manufacturer: Optional[bool] = None
    year_established: Optional[int] = None
    number_of_employees: Optional[int] = None
    description: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    business_sector: Optional[str] = None
    photo_url: Optional[str] = None
    supplier: Optional[Supplier] = None
