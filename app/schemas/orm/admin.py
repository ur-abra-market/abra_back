from .core import ORMSchema, mixins


class Admin(mixins.UserIDMixin, ORMSchema):
    ...
