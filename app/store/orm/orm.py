from __future__ import annotations

from orm import CategoryModel, UserCredentialsModel, UserModel

from .base import ORMAccessor


class ORM:
    def __init__(self) -> None:
        self.categories: ORMAccessor[CategoryModel] = ORMAccessor(CategoryModel)
        self.users: ORMAccessor[UserModel] = ORMAccessor(UserModel)
        self.users_credentials: ORMAccessor[UserCredentialsModel] = ORMAccessor(UserCredentialsModel)
