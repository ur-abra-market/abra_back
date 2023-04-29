from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, bool_false, mixins

if TYPE_CHECKING:
    from .admin import AdminModel
    from .seller import SellerModel
    from .supplier import SupplierModel
    from .user_credentials import UserCredentialsModel
    from .user_notification import UserNotificationModel


class UserModel(
    mixins.EmailMixin, mixins.NameMixin, mixins.PhoneMixin, mixins.TimestampMixin, ORMModel
):
    is_supplier: Mapped[bool]
    is_verified: Mapped[bool_false]
    is_deleted: Mapped[bool_false]

    admin: Mapped[Optional[AdminModel]] = relationship(back_populates="user")
    credentials: Mapped[Optional[UserCredentialsModel]] = relationship(back_populates="user")
    notification: Mapped[Optional[UserNotificationModel]] = relationship(back_populates="user")

    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="user")
    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="user")
