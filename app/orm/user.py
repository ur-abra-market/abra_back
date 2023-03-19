from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, relationship

from app.orm.core import ORMModel, mixins, str_30

if TYPE_CHECKING:
    from app.orm.seller import SellerModel
    from app.orm.supplier import SupplierModel
    from app.orm.user_address import UserAddressModel
    from app.orm.user_credentials import UserCredentialsModel
    from app.orm.user_image import UserImageModel
    from app.orm.user_notification import UserNotificationModel


class UserModel(mixins.EmailMixin, mixins.PhoneMixin, mixins.TimestampMixin, ORMModel):
    first_name: Mapped[Optional[str_30]]
    last_name: Mapped[Optional[str_30]]

    is_supplier: Mapped[bool]

    credentials: Mapped[Optional[UserCredentialsModel]] = relationship(UserCredentialsModel)
    images: Mapped[List[UserImageModel]] = relationship(UserImageModel)
    addresses: Mapped[List[UserAddressModel]] = relationship(UserAddressModel)
    notification: Mapped[Optional[UserNotificationModel]] = relationship(UserNotificationModel)

    seller: Mapped[Optional[SellerModel]] = relationship(SellerModel, back_populates="user")
    supplier: Mapped[Optional[SupplierModel]] = relationship(SupplierModel, back_populates="user")

    @hybrid_property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
