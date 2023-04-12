from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, bool_false, mixins, str_30

if TYPE_CHECKING:
    from .seller import SellerModel
    from .supplier import SupplierModel
    from .user_address import UserAddressModel
    from .user_credentials import UserCredentialsModel
    from .user_image import UserImageModel
    from .user_notification import UserNotificationModel


class UserModel(mixins.EmailMixin, mixins.PhoneMixin, mixins.TimestampMixin, ORMModel):
    first_name: Mapped[Optional[str_30]]
    last_name: Mapped[Optional[str_30]]

    is_supplier: Mapped[bool]
    is_verified: Mapped[bool_false]

    credentials: Mapped[Optional[UserCredentialsModel]] = relationship()
    image: Mapped[Optional[UserImageModel]] = relationship()
    addresses: Mapped[List[UserAddressModel]] = relationship(back_populates="user")
    notification: Mapped[Optional[UserNotificationModel]] = relationship()

    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="user")
    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="user")

    @hybrid_property
    def full_name(self) -> Optional[str]:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        if self.first_name:
            return f"{self.first_name}"
        if self.last_name:
            return f"{self.last_name}"
        return None
