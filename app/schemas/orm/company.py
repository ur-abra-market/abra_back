from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .company_image import CompanyImage
    from .country import Country
    from .supplier import Supplier


class Company(mixins.BusinessEmailMixin, mixins.PhoneMixin, ORMSchema):
    name: str
    is_manufacturer: bool = False
    year_established: int
    number_employees: int
    description: str
    address: str
    logo_url: str
    business_sector: str
    country: Country
    images: Optional[List[CompanyImage]] = None
    supplier: Optional[Supplier] = None
