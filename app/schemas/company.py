from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .category import Category
    from .company_image import CompanyImage
    from .company_phone import CompanyPhone
    from .country import Country
    from .employees_number import EmployeesNumber
    from .supplier import Supplier


class Company(mixins.BusinessEmailMixin, mixins.PhoneMixin, ORMSchema):
    name: str
    is_manufacturer: bool = False
    year_established: int
    number_employees_id: int
    description: Optional[str]
    address: Optional[str]
    logo_url: Optional[str]

    country: Optional[Country] = None
    phone: Optional[CompanyPhone] = None
    images: Optional[List[CompanyImage]] = None
    supplier: Optional[Supplier] = None
    employees_number: Optional[EmployeesNumber] = None
    business_sectors: Optional[Category] = None
