from app.orm.core import ORMModel, mixins


class AdminModel(mixins.UserIDMixin, ORMModel):
    ...
