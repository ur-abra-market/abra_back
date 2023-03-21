from .core import ORMModel, mixins


class SellerFavoriteModel(mixins.SellerIDMixin, mixins.ProductIDMixin, ORMModel):
    ...
