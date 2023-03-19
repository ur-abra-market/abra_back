from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from app.schemas.orm.schema import ORMSchema
from pydantic import EmailStr

if TYPE_CHECKING:
    from app.schemas.orm.supplier import Supplier


class Company(ORMSchema):
    name: str
    business_email: Optional[EmailStr]
    phone: str
    is_manufacturer: Optional[bool] = None
    year_established: Optional[int] = None
    number_of_employees: Optional[int] = None
    description: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    business_sector: Optional[str] = None
    photo_url: Optional[str] = None
    supplier: Optional[Supplier] = None
