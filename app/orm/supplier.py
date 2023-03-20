from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.orm.core import ORMModel, decimal_2_1, mixins, str_25

if TYPE_CHECKING:
    from app.orm.company import CompanyModel
    from app.orm.product import ProductModel
    from app.orm.user import UserModel


class SupplierModel(mixins.UserIDMixin, ORMModel):
    license_number: Mapped[Optional[str_25]]
    grade_average: Mapped[decimal_2_1] = mapped_column(default=0.0)
    additional_info: Mapped[Optional[str]]

    user: Mapped[Optional[UserModel]] = relationship(back_populates="supplier")
    company: Mapped[Optional[CompanyModel]] = relationship(back_populates="supplier")
    products: Mapped[List[ProductModel]] = relationship(back_populates="supplier")
