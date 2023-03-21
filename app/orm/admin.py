from .core import ORMModel, mixins


class AdminModel(mixins.UserIDMixin, ORMModel):
    ...
