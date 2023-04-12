from __future__ import annotations

from typing import List, Optional

from ..orm import UserAddress
from ..schema import ApplicationORMSchema
from .user_info import UserInfo


class UserAddressesInfo(ApplicationORMSchema):
    user: UserInfo
    addresses: Optional[List[UserAddress]] = []
