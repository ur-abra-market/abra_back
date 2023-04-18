from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .company_image import CompanyImage
    from .supplier import Supplier


class Company(mixins.BusinessEmailMixin, mixins.PhoneMixin, ORMSchema):
    name: Optional[str] = None
    is_manufacturer: bool = False
    year_established: Optional[int] = None
    number_of_employees: Optional[int] = None
    description: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    business_sector: Optional[str] = None
    images: Optional[List[CompanyImage]] = None
    supplier: Optional[Supplier] = None
