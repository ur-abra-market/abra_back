from sqlalchemy import and_, event, func, select
from sqlalchemy.orm import relationship

from .product import ProductModel
from .product_prices import ProductPriceModel


@event.listens_for(ProductModel, "before_mapper_configured")
def _configure_ab_product_relationship(mapper, cls):
    price = (ProductPriceModel.value - ProductPriceModel.value * ProductPriceModel.discount).label(
        "price"
    )
    min_price_subquery = (
        select(ProductPriceModel.product_id, func.min(price).label("min_price"))
        .group_by(ProductPriceModel.product_id)
        .subquery()
    )
    max_price_subquery = (
        select(ProductPriceModel.product_id, func.max(price).label("max_price"))
        .group_by(ProductPriceModel.product_id)
        .subquery()
    )
    ProductModel.min_price = relationship(
        ProductPriceModel,
        secondary=min_price_subquery,
        primaryjoin=ProductModel.id == ProductPriceModel.product_id,
        secondaryjoin=and_(
            ProductPriceModel.product_id == min_price_subquery.c.product_id,
            price == min_price_subquery.c.min_price,
        ),
        uselist=False,
        viewonly=True,
        lazy="selectin",
    )
    ProductModel.max_price = relationship(
        ProductPriceModel,
        secondary=max_price_subquery,
        primaryjoin=ProductModel.id == ProductPriceModel.product_id,
        secondaryjoin=and_(
            ProductPriceModel.product_id == max_price_subquery.c.product_id,
            price == max_price_subquery.c.max_price,
        ),
        uselist=False,
        viewonly=True,
        lazy="selectin",
    )
